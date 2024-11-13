"""Airzone Local API."""

from __future__ import annotations

import asyncio
from asyncio import Lock, Semaphore
from dataclasses import dataclass
from enum import IntEnum
from json import JSONDecodeError
import logging
from typing import Any, cast

from aiohttp import ClientConnectorError, ClientSession, ClientTimeout
from aiohttp.client_reqrep import ClientResponse
from packaging.version import Version

from .common import OperationMode, get_system_zone_id, json_dumps, validate_mac_address
from .const import (
    API_ACS_MAX_TEMP,
    API_ACS_MIN_TEMP,
    API_ACS_ON,
    API_ACS_SET_POINT,
    API_ACS_TEMP,
    API_DATA,
    API_DEMO,
    API_DHW_PARAMS,
    API_ERROR_HOT_WATER_NOT_CONNECTED,
    API_ERROR_IAQ_SENSOR_ID_NOT_AVAILABLE,
    API_ERROR_METHOD_NOT_SUPPORTED,
    API_ERROR_REQUEST_MALFORMED,
    API_ERROR_SYSTEM_ID_NOT_AVAILABLE,
    API_ERROR_SYSTEM_ID_OUT_RANGE,
    API_ERROR_ZONE_ID_NOT_AVAILABLE,
    API_ERROR_ZONE_ID_NOT_PROVIDED,
    API_ERROR_ZONE_ID_OUT_RANGE,
    API_ERRORS,
    API_HVAC,
    API_INTEGRATION,
    API_MAC,
    API_NO_FEEDBACK_PARAMS,
    API_SYSTEM_ID,
    API_SYSTEM_PARAMS,
    API_SYSTEMS,
    API_V1,
    API_VERSION,
    API_WEBSERVER,
    API_ZONE_ID,
    API_ZONE_PARAMS,
    AZD_HOT_WATER,
    AZD_SYSTEMS,
    AZD_SYSTEMS_NUM,
    AZD_VERSION,
    AZD_WEBSERVER,
    AZD_ZONES,
    AZD_ZONES_NUM,
    DEFAULT_PORT,
    DEFAULT_SYSTEM_ID,
    HTTP_CALL_TIMEOUT,
    HTTP_MAX_REQUESTS,
    HTTP_QUIRK_VERSION,
    RAW_DEMO,
    RAW_DHW,
    RAW_HEADERS,
    RAW_HTTP,
    RAW_HVAC,
    RAW_INTEGRATION,
    RAW_QUIRKS,
    RAW_REASON,
    RAW_STATUS,
    RAW_SYSTEMS,
    RAW_VERSION,
    RAW_WEBSERVER,
)
from .exceptions import (
    APIError,
    HotWaterNotAvailable,
    IaqSensorNotAvailable,
    InvalidHost,
    InvalidMethod,
    InvalidParam,
    InvalidSystem,
    InvalidZone,
    RequestMalformed,
    SystemNotAvailable,
    SystemOutOfRange,
    ZoneNotAvailable,
    ZoneNotProvided,
    ZoneOutOfRange,
)
from .hotwater import HotWater
from .http import AirzoneHttp
from .system import System
from .webserver import WebServer
from .zone import Zone

_LOGGER = logging.getLogger(__name__)


class ApiFeature(IntEnum):
    """Supported features of the Airzone Local API."""

    HVAC = 0
    SYSTEMS = 1
    WEBSERVER = 2
    HOT_WATER = 4


@dataclass
class ConnectionOptions:
    """Airzone Local API options for connection."""

    host: str
    port: int = DEFAULT_PORT
    system_id: int = DEFAULT_SYSTEM_ID
    http_quirks: bool = False


class AirzoneLocalApi:
    """Airzone Local API device representation."""

    def __init__(
        self,
        aiohttp_session: ClientSession,
        options: ConnectionOptions,
    ):
        """Device init."""
        self._api_raw_data: dict[str, Any] = {
            RAW_DEMO: {},
            RAW_DHW: {},
            RAW_HVAC: {},
            RAW_HTTP: {},
            RAW_INTEGRATION: {},
            RAW_SYSTEMS: {},
            RAW_VERSION: {},
            RAW_WEBSERVER: {},
        }
        self._api_raw_data_lock = Lock()
        self._api_semaphore: Semaphore = Semaphore(HTTP_MAX_REQUESTS)
        self._api_timeout: ClientTimeout = ClientTimeout(total=HTTP_CALL_TIMEOUT)
        self._first_update: bool = True
        self.aiohttp_session = aiohttp_session
        self.api_features: int = ApiFeature.HVAC
        self.api_features_checked = False
        self.api_features_lock = Lock()
        self.hotwater: HotWater | None = None
        self.http = AirzoneHttp()
        self.http_quirks_needed = True
        self.options = options
        self.systems: dict[int, System] = {}
        self.version: str | None = None
        self.webserver: WebServer | None = None
        self.zones: dict[str, Zone] = {}

    def handle_empty_response(self, function: str, request: str) -> None:
        """Handle Airzone API empty response."""
        error_str = f"{function}: empty {request} API response"
        if self._first_update:
            raise APIError(error_str)
        _LOGGER.error(error_str)

    @staticmethod
    def handle_errors(errors: list[dict[str, str]]) -> None:
        """Handle API errors."""
        for error in errors:
            for key, val in error.items():
                if val == API_ERROR_HOT_WATER_NOT_CONNECTED:
                    raise HotWaterNotAvailable(f"{key}: {val}")
                if val == API_ERROR_IAQ_SENSOR_ID_NOT_AVAILABLE:
                    raise IaqSensorNotAvailable(f"{key}: {val}")
                if val == API_ERROR_METHOD_NOT_SUPPORTED:
                    raise InvalidMethod(f"{key}: {val}")
                if val == API_ERROR_REQUEST_MALFORMED:
                    raise RequestMalformed(f"{key}: {val}")
                if val == API_ERROR_SYSTEM_ID_NOT_AVAILABLE:
                    raise SystemNotAvailable(f"{key}: {val}")
                if val == API_ERROR_SYSTEM_ID_OUT_RANGE:
                    raise SystemOutOfRange(f"{key}: {val}")
                if val == API_ERROR_ZONE_ID_OUT_RANGE:
                    raise ZoneOutOfRange(f"{key}: {val}")
                if val == API_ERROR_ZONE_ID_NOT_AVAILABLE:
                    raise ZoneNotAvailable(f"{key}: {val}")
                if val == API_ERROR_ZONE_ID_NOT_PROVIDED:
                    raise ZoneNotProvided(f"{key}: {val}")
                raise APIError(f"{key}: {val}")

    def http_quirks_enabled(self) -> bool:
        """API expects HTTP headers + body on the same TCP segment."""
        return self.options.http_quirks or self.http_quirks_needed

    async def aiohttp_request(
        self, method: str, path: str, data: Any | None = None
    ) -> dict[str, Any] | None:
        """Perform aiohttp request."""
        async with self._api_semaphore:
            try:
                resp: ClientResponse = await self.aiohttp_session.request(
                    method,
                    f"http://{self.options.host}:{self.options.port}/{path}",
                    data=json_dumps(data),
                    headers={"Content-Type": "text/json"},
                    timeout=self._api_timeout,
                )
            except ClientConnectorError as err:
                raise InvalidHost(err) from err

            try:
                resp_json = await resp.json(content_type=None)
            except JSONDecodeError as err:
                raise InvalidHost(err) from err

        _LOGGER.debug("aiohttp response: %s", resp_json)
        if resp.status != 200:
            if resp_json is not None:
                resp_err = resp_json.get(API_ERRORS)
            else:
                resp_err = None
            if resp_err is not None:
                self.handle_errors(resp_err)
            raise APIError(f"HTTP status: {resp.status}")

        return cast(dict[str, Any], resp_json)

    async def http_quirks_request(
        self, method: str, path: str, data: Any | None = None
    ) -> dict[str, Any] | None:
        """Perform http quirks request."""
        async with self._api_semaphore:
            resp = await self.http.request(
                method,
                f"http://{self.options.host}:{self.options.port}/{path}",
                data=json_dumps(data),
                headers={
                    "Content-Type": "text/json",
                },
                timeout=HTTP_CALL_TIMEOUT,
            )

            resp_json = resp.json()

        _LOGGER.debug("aiohttp response: %s", resp_json)
        if resp.status != 200:
            if resp_json is not None:
                resp_err = resp_json.get(API_ERRORS)
            else:
                resp_err = None
            if resp_err is not None:
                self.handle_errors(resp_err)
            raise APIError(f"HTTP status: {resp.status}")

        if path.endswith(API_VERSION):
            async with self._api_raw_data_lock:
                self._api_raw_data[RAW_HTTP][RAW_HEADERS] = resp.header_map
                self._api_raw_data[RAW_HTTP][RAW_REASON] = resp.reason
                self._api_raw_data[RAW_HTTP][RAW_STATUS] = resp.status
                self._api_raw_data[RAW_HTTP][RAW_VERSION] = resp.version

        return cast(dict[str, Any], resp_json)

    async def http_request(
        self, method: str, path: str, data: Any | None = None
    ) -> dict[str, Any] | None:
        """Device HTTP request."""
        _LOGGER.debug("http_request: /%s (params=%s)", path, data)

        if self.http_quirks_enabled():
            return await self.http_quirks_request(method, path, data)
        return await self.aiohttp_request(method, path, data)

    def update_dhw(self, data: dict[str, Any]) -> None:
        """Gather Domestic Hot Water data."""
        dhw = data.get(API_DATA, {})
        if self.hotwater is not None:
            self.hotwater.update_data(dhw)
        else:
            self.hotwater = HotWater(dhw)

    def update_systems(self, data: dict[str, Any] | None) -> None:
        """Gather Systems data."""
        if data is None:
            self.handle_empty_response("update_systems", "Systems")
            return
        api_systems = data.get(API_SYSTEMS)
        if api_systems is None:
            raise APIError(f"update_systems: {API_SYSTEMS} not in API response")
        for api_system in api_systems:
            system = self.get_system(api_system[API_SYSTEM_ID])
            if system:
                system.update_data(api_system)

    def update_webserver(self, data: dict[str, Any]) -> None:
        """Gather WebServer data."""
        if self.webserver is not None:
            self.webserver.update_data(data)
        else:
            self.webserver = WebServer(data)

    def check_dhw(self, dhw: dict[str, Any]) -> bool:
        """Check Airzone Domestic Hot Water validity."""
        return all(
            [
                dhw.get(API_ACS_MAX_TEMP, 0) != 0,
                dhw.get(API_ACS_MIN_TEMP, 0) != 0,
                API_ACS_ON in dhw,
                dhw.get(API_ACS_SET_POINT, 0) != 0,
                dhw.get(API_ACS_TEMP, 0) != 0,
                dhw.get(API_SYSTEM_ID, 0) == 0,
            ]
        )

    async def check_feature_dhw(self, update: bool) -> None:
        """Check DHW feature."""
        try:
            dhw = await self.get_dhw()
            if dhw is None:
                raise APIError("check_feature_dhw: empty API response")
            if self.check_dhw(dhw.get(API_DATA, {})):
                await self.set_api_feature(ApiFeature.HOT_WATER)
                if update:
                    self.update_dhw(dhw)
        except (HotWaterNotAvailable, ZoneNotProvided):
            pass

    async def check_feature_systems(self, update: bool) -> None:
        """Check Systems feature."""
        try:
            systems = await self.get_hvac_systems()
            if systems is None:
                raise APIError("check_feature_systems: empty API response")
            if API_SYSTEMS in systems:
                await self.set_api_feature(ApiFeature.SYSTEMS)
                if update:
                    self.update_systems(systems)
        except (SystemOutOfRange, ZoneNotProvided):
            pass

    async def check_feature_version(self) -> None:
        """Check Version feature."""
        try:
            version_data = await self.get_version()
            if version_data is None:
                raise APIError("check_feature_version: empty API response")
            version_str = version_data.get(API_VERSION)
            if version_str is not None:
                self.version = version_str
                self.http_quirks_needed = Version(version_str) < HTTP_QUIRK_VERSION
                async with self._api_raw_data_lock:
                    self._api_raw_data[RAW_HTTP][RAW_QUIRKS] = self.http_quirks_needed
        except InvalidMethod:
            pass

    async def check_feature_webserver(self) -> None:
        """Check WebServer feature."""
        try:
            self.webserver = None
            webserver = await self.get_webserver()
            if webserver is None:
                raise APIError("check_feature_webserver: empty API response")
            if validate_mac_address(webserver.get(API_MAC)):
                await self.set_api_feature(ApiFeature.WEBSERVER)
                self.update_webserver(webserver)
        except InvalidMethod:
            pass

    async def check_features(self, update: bool) -> None:
        """Check Airzone API features."""
        # Check version and toggle HTTP quirks first.
        await self.check_feature_version()

        tasks = [
            asyncio.create_task(self.check_feature_webserver()),
            asyncio.create_task(self.check_feature_systems(update)),
            asyncio.create_task(self.check_feature_dhw(update)),
        ]
        await asyncio.gather(*tasks)

        self.api_features_checked = True

    async def update_feature_dhw(self) -> None:
        """Update DHW feature."""
        dhw = await self.get_dhw()
        if dhw is not None:
            self.update_dhw(dhw)
        else:
            self.handle_empty_response("update_features", "DHW")

    async def update_feature_systems(self) -> None:
        """Update Systems feature."""
        systems = await self.get_hvac_systems()
        if systems is not None:
            self.update_systems(systems)
        else:
            self.handle_empty_response("update_features", "Systems")

    async def update_feature_webserver(self) -> None:
        """Update WebServer feature."""
        webserver = await self.get_webserver()
        if webserver is not None:
            self.update_webserver(webserver)
        else:
            self.handle_empty_response("update_features", "WebServer")

    async def update_features(self) -> None:
        """Update Airzone features data."""
        tasks = []

        if not self.api_features_checked:
            tasks += [asyncio.create_task(self.check_features(True))]
        else:
            if self.api_feature(ApiFeature.HOT_WATER):
                tasks += [asyncio.create_task(self.update_feature_dhw())]

            if self.api_feature(ApiFeature.SYSTEMS):
                tasks += [asyncio.create_task(self.update_feature_systems())]

            if self.api_feature(ApiFeature.WEBSERVER):
                tasks += [asyncio.create_task(self.update_feature_webserver())]

        await asyncio.gather(*tasks)

    async def validate(self) -> str | None:
        """Validate Airzone API."""
        self._first_update = True

        await self.check_features(False)

        response = await self.get_hvac()
        if response is None:
            raise APIError("validate: empty HVAC API response")
        if self.options.system_id == DEFAULT_SYSTEM_ID:
            if API_SYSTEMS not in response:
                raise InvalidHost(f"validate: {API_SYSTEMS} not in API response")
        elif API_DATA not in response:
            raise InvalidHost(f"validate: {API_DATA} not in API response")

        if self.webserver:
            return self.webserver.get_mac()

        return None

    async def update(self) -> None:
        """Gather Airzone data."""

        hvac = await self.get_hvac()
        if hvac is None:
            self.handle_empty_response("update", "HVAC")
            return

        for system in self.systems.values():
            system.set_available(False)
        for zone in self.zones.values():
            zone.set_available(False)

        if self.options.system_id == DEFAULT_SYSTEM_ID:
            hvac_systems = hvac.get(API_SYSTEMS)
            if hvac_systems is None:
                raise APIError(f"update: {API_SYSTEMS} not in API response")
            for system_data in hvac_systems:
                self.parse_system_zones(system_data)
        else:
            self.parse_system_zones(hvac)

        await self.update_features()

        self._first_update = False

    def parse_system_zones(self, system_data: dict[str, Any]) -> None:
        """Parse all zones from system data."""

        system_zones: list[dict[str, Any]] = system_data.get(API_DATA, [])
        for zone_data in system_zones:
            system_id = int(zone_data.get(API_SYSTEM_ID, 0))
            if system_id > 0:
                if system_id not in self.systems:
                    self.systems[system_id] = System(system_id, zone_data)
                else:
                    self.systems[system_id].update_zone_data(zone_data)

                zone_id = int(zone_data.get(API_ZONE_ID, 0))
                if zone_id > 0:
                    system_zone_id = get_system_zone_id(system_id, zone_id)

                    if system_zone_id not in self.zones:
                        _zone = Zone(system_id, zone_id, zone_data)
                        self.zones[system_zone_id] = _zone
                        self.systems[system_id].add_zone(_zone)
                    else:
                        self.zones[system_zone_id].update_data(zone_data)

                    self.update_system_from_zone(
                        self.systems[system_id], self.zones[system_zone_id]
                    )

        self.update_zones_from_master_zone()

    def update_system_from_zone(self, system: System, zone: Zone) -> None:
        """Update system data from zone."""
        if zone.get_master():
            if (eco_adapt := zone.get_eco_adapt()) is not None:
                system.set_eco_adapt(eco_adapt)

            system.set_master_system_zone(zone.get_system_zone_id())
            system.set_master_zone(zone.get_id())

            if (mode := zone.get_mode()) is not None:
                system.set_mode(mode)

            system.set_modes(zone.get_modes())
        else:
            if system.get_eco_adapt() is None:
                system.set_eco_adapt(zone.get_eco_adapt())
            if system.get_mode() is None:
                system.set_mode(zone.get_mode())
            if len(system.get_modes()) == 0:
                system.set_modes(zone.get_modes())

    def update_zones_from_master_zone(self) -> None:
        """Update slave zones data with their master zone."""
        for zone in self.zones.values():
            system_id = zone.get_system_id()

            if system_id is not None and not zone.get_master():
                modes: list[OperationMode] = []

                master_id = zone.get_master_zone()
                if master_id is None:
                    system = self.get_system(system_id)
                    modes = system.get_modes()
                else:
                    master_zone = self.get_zone(system_id, master_id)
                    modes = master_zone.get_modes()

                if len(modes) > 0:
                    zone.set_modes(modes)

    async def get_demo(self) -> dict[str, Any] | None:
        """Return Airzone demo."""
        res = await self.http_request(
            "POST",
            f"{API_V1}/{API_DEMO}",
        )
        await self.set_api_raw_data(RAW_DEMO, res)
        return res

    async def get_dhw(
        self, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """Return Airzone DHW (Domestic Hot Water)."""
        if not params:
            params = {
                API_SYSTEM_ID: 0,
            }
        res = await self.http_request(
            "POST",
            f"{API_V1}/{API_HVAC}",
            params,
        )
        await self.set_api_raw_data(RAW_DHW, res)
        return res

    async def get_hvac_systems(
        self, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """Return Airzone HVAC systems."""
        if not params:
            params = {
                API_SYSTEM_ID: 127,
            }
        res = await self.http_request(
            "POST",
            f"{API_V1}/{API_HVAC}",
            params,
        )
        await self.set_api_raw_data(RAW_SYSTEMS, res)
        return res

    async def get_hvac(
        self, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """Return Airzone HVAC zones."""
        if not params:
            params = {
                API_SYSTEM_ID: self.options.system_id,
                API_ZONE_ID: 0,
            }
        res = await self.http_request(
            "POST",
            f"{API_V1}/{API_HVAC}",
            params,
        )
        await self.set_api_raw_data(RAW_HVAC, res)
        return res

    async def get_integration(self) -> dict[str, Any] | None:
        """Return Airzone integration."""
        res = await self.http_request(
            "POST",
            f"{API_V1}/{API_INTEGRATION}",
        )
        await self.set_api_raw_data(RAW_INTEGRATION, res)
        return res

    async def get_version(self) -> dict[str, Any] | None:
        """Return Airzone Local API version."""
        res = await self.http_request(
            "POST",
            f"{API_V1}/{API_VERSION}",
        )
        await self.set_api_raw_data(RAW_VERSION, res)
        return res

    async def get_webserver(self) -> dict[str, Any] | None:
        """Return Airzone WebServer."""
        res = await self.http_request(
            "POST",
            f"{API_V1}/{API_WEBSERVER}",
        )
        await self.set_api_raw_data(RAW_WEBSERVER, res)
        return res

    async def put_hvac(self, params: dict[str, Any]) -> dict[str, Any] | None:
        """Perform a PUT request to update HVAC parameters."""
        return await self.http_request(
            "PUT",
            f"{API_V1}/{API_HVAC}",
            params,
        )

    async def set_api_feature(self, feature: int) -> None:
        """Set API feature."""
        async with self.api_features_lock:
            self.api_features |= feature

    async def set_api_raw_data(self, key: str, data: dict[str, Any] | None) -> None:
        """Save API raw data if not empty."""
        if data is not None:
            async with self._api_raw_data_lock:
                self._api_raw_data[key] = data

    async def set_dhw_parameters(self, params: dict[str, Any]) -> dict[str, Any]:
        """Set Airzone Hot Water parameters and handle response."""
        res = await self.put_hvac(params)

        if res is None:
            raise APIError("set_dhw: empty HVAC API response")

        if API_DATA not in res:
            if API_ERRORS in res:
                self.handle_errors(res[API_ERRORS])
            raise APIError(f"set_dhw: {API_DATA} not in API response")

        if self.hotwater is not None:
            data: dict[str, Any] = res.get(API_DATA, {})

            for key, value in data.items():
                if key in API_DHW_PARAMS:
                    self.hotwater.set_param(key, value)

        return res

    async def set_hvac_parameters(self, params: dict[str, Any]) -> dict[str, Any]:
        """Set Airzone HVAC parameters and handle response."""
        res = await self.put_hvac(params)

        if res is None:
            raise APIError("set_hvac: empty HVAC API response")

        if API_DATA not in res:
            if API_ERRORS in res:
                self.handle_errors(res[API_ERRORS])
            raise APIError(f"set_hvac: {API_DATA} not in API response")

        data: dict[str, Any] = res[API_DATA][0]

        for param in API_NO_FEEDBACK_PARAMS:
            value = params.get(param)
            if value is not None and param not in data:
                _LOGGER.debug("set_hvac: forcing %s=%s", param, value)
                data[param] = value

        for key, value in params.items():
            if (
                key in [API_SYSTEM_ID, API_ZONE_ID]
                and value != 0
                and data.get(key) != value
            ):
                if key == API_SYSTEM_ID:
                    raise InvalidSystem(
                        f"set_hvac: System mismatch: {data.get(key)} vs {value}"
                    )
                if key == API_ZONE_ID:
                    raise InvalidZone(
                        f"set_hvac: Zone mismatch: {data.get(key)} vs {value}"
                    )

            if key not in data:
                raise InvalidParam(f"set_hvac: param not in data: {key}={value}")

        system = self.get_system(data[API_SYSTEM_ID])
        zone = self.get_zone(data[API_SYSTEM_ID], data[API_ZONE_ID])
        for key, value in data.items():
            if key in API_SYSTEM_PARAMS:
                system.set_param(key, value)
            elif key in API_ZONE_PARAMS:
                zone.set_param(key, value)

        return res

    def api_feature(self, feature: int) -> bool:
        """Get API feature."""
        return bool(self.api_features & feature)

    def raw_data(self) -> dict[str, Any]:
        """Return raw Airzone API data."""
        return self._api_raw_data

    def data(self) -> dict[str, Any]:
        """Return Airzone device data."""
        data: dict[str, Any] = {}

        if self.hotwater is not None:
            data[AZD_HOT_WATER] = self.hotwater.data()

        data[AZD_SYSTEMS_NUM] = self.num_systems()
        if len(self.systems) > 0:
            systems: dict[int, Any] = {}
            for system_id, system in self.systems.items():
                systems[system_id] = system.data()
            data[AZD_SYSTEMS] = systems

        if self.webserver is not None:
            data[AZD_WEBSERVER] = self.webserver.data()

        data[AZD_ZONES_NUM] = self.num_zones()
        if len(self.zones) > 0:
            zones: dict[str, Any] = {}
            for system_zone_id, zone in self.zones.items():
                zones[system_zone_id] = zone.data()
            data[AZD_ZONES] = zones

        if self.version is not None:
            data[AZD_VERSION] = self.version

        return data

    def get_system(self, system_id: int) -> System:
        """Return Airzone system."""
        if system_id not in self.systems:
            raise InvalidSystem(f"System {system_id} not present")
        return self.systems[system_id]

    def get_zone(self, system_id: int, zone_id: int) -> Zone:
        """Return Airzone zone."""
        system_zone_id = get_system_zone_id(system_id, zone_id)
        if system_zone_id not in self.zones:
            raise InvalidZone(f"Zone {system_zone_id} not present")
        return self.zones[system_zone_id]

    def num_systems(self) -> int:
        """Return number of systems."""
        return len(self.systems)

    def num_zones(self) -> int:
        """Return number of zones."""
        return len(self.zones)
