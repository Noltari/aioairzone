"""Airzone Local API."""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
import json
from json import JSONDecodeError
import logging
from typing import Any, cast

from aiohttp import ClientConnectorError, ClientSession
from aiohttp.client_reqrep import ClientResponse

from .common import OperationMode, get_system_zone_id
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
    AZD_NEW_SYSTEMS,
    AZD_NEW_ZONES,
    AZD_SYSTEMS,
    AZD_SYSTEMS_NUM,
    AZD_VERSION,
    AZD_WEBSERVER,
    AZD_ZONES,
    AZD_ZONES_NUM,
    DEFAULT_PORT,
    DEFAULT_SYSTEM_ID,
    HTTP_CALL_TIMEOUT,
    RAW_DEMO,
    RAW_DHW,
    RAW_HVAC,
    RAW_INTEGRATION,
    RAW_SYSTEMS,
    RAW_VERSION,
    RAW_WEBSERVER,
)
from .exceptions import (
    APIError,
    HotWaterNotAvailable,
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


class AirzoneLocalApi:
    """Airzone Local API device representation."""

    def __init__(
        self,
        aiohttp_session: ClientSession,
        options: ConnectionOptions,
    ):
        """Device init."""
        self._api_raw_data: dict[str, Any] = {}
        self._first_update: bool = True
        self._new_systems: list[str] = []
        self._new_zones: list[str] = []
        self.aiohttp_session = aiohttp_session
        self.api_features: int = ApiFeature.HVAC
        self.api_features_checked = False
        self.hotwater: HotWater | None = None
        self.options = options
        self.systems: dict[int, System] = {}
        self.version: str | None = None
        self.webserver: WebServer | None = None
        self.zones: dict[str, Zone] = {}

    @staticmethod
    def handle_errors(errors: list[dict[str, str]]) -> None:
        """Handle API errors."""
        for error in errors:
            for key, val in error.items():
                if val == API_ERROR_HOT_WATER_NOT_CONNECTED:
                    raise HotWaterNotAvailable(f"{key}: {val}")
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

    async def http_request(
        self, method: str, path: str, data: Any | None = None
    ) -> dict[str, Any]:
        """Device HTTP request."""
        _LOGGER.debug("aiohttp request: /%s (params=%s)", path, data)

        try:
            resp: ClientResponse = await self.aiohttp_session.request(
                method,
                f"http://{self.options.host}:{self.options.port}/{path}",
                data=json.dumps(data),
                timeout=HTTP_CALL_TIMEOUT,
            )
        except ClientConnectorError as err:
            raise InvalidHost(err) from err

        try:
            resp_json = await resp.json(content_type=None)
        except JSONDecodeError as err:
            raise InvalidHost(err) from err

        _LOGGER.debug("aiohttp response: %s", resp_json)
        if resp.status != 200:
            if API_ERRORS in resp_json:
                self.handle_errors(resp_json[API_ERRORS])
            raise APIError(f"HTTP status: {resp.status}")

        return cast(dict[str, Any], resp_json)

    def update_dhw(self, data: dict[str, Any]) -> None:
        """Gather Domestic Hot Water data."""
        dhw = data.get(API_DATA, {})
        if self.hotwater is not None:
            self.hotwater.update_data(dhw)
        else:
            self.hotwater = HotWater(dhw)

    def update_systems(self, data: dict[str, Any]) -> None:
        """Gather Systems data."""
        for api_system in data[API_SYSTEMS]:
            system = self.get_system(api_system[API_SYSTEM_ID])
            if system:
                system.update_data(api_system)

    def update_webserver(self, data: dict[str, Any]) -> None:
        """Gather WebServer data."""
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

    async def check_features(self, update: bool) -> None:
        """Check Airzone API features."""
        try:
            self.webserver = None
            webserver = await self.get_webserver()
            if API_MAC in webserver:
                self.api_features |= ApiFeature.WEBSERVER
                self.update_webserver(webserver)
        except InvalidMethod:
            pass

        try:
            systems = await self.get_hvac_systems()
            if API_SYSTEMS in systems:
                self.api_features |= ApiFeature.SYSTEMS
                if update:
                    self.update_systems(systems)
        except (SystemOutOfRange, ZoneNotProvided):
            pass

        try:
            dhw = await self.get_dhw()
            if self.check_dhw(dhw.get(API_DATA, {})):
                self.api_features |= ApiFeature.HOT_WATER
                if update:
                    self.update_dhw(dhw)
        except (HotWaterNotAvailable, ZoneNotProvided):
            pass

        try:
            version = await self.get_version()
            if API_VERSION in version:
                self.version = version[API_VERSION]
        except InvalidMethod:
            pass

        self.api_features_checked = True

    async def update_features(self) -> None:
        """Gather Airzone features data."""
        if not self.api_features_checked:
            await self.check_features(True)
        else:
            if self.api_features & ApiFeature.HOT_WATER:
                self.update_dhw(await self.get_dhw())

            if self.api_features & ApiFeature.SYSTEMS:
                self.update_systems(await self.get_hvac_systems())

            if self.api_features & ApiFeature.WEBSERVER:
                self.update_webserver(await self.get_webserver())

    async def validate(self) -> str | None:
        """Validate Airzone API."""
        self._first_update = True

        await self.check_features(False)

        response = await self.get_hvac()
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

        for system in self.systems.values():
            system.set_available(False)
        for zone in self.zones.values():
            zone.set_available(False)

        hvac = await self.get_hvac()
        if self.options.system_id == DEFAULT_SYSTEM_ID:
            for system_data in hvac[API_SYSTEMS]:
                self.parse_system_zones(system_data)
        else:
            self.parse_system_zones(hvac)

        await self.update_features()

        self._first_update = False

    def parse_system_zones(self, system_data: dict[str, Any]) -> None:
        """Parse all zones from system data."""
        self._new_systems = []
        self._new_zones = []

        system_zones: list[dict[str, Any]] = system_data.get(API_DATA, [])
        for zone_data in system_zones:
            system_id = int(zone_data.get(API_SYSTEM_ID, 0))
            if system_id > 0:
                if system_id not in self.systems:
                    self.systems[system_id] = System(system_id, zone_data)
                    self._new_systems += [str(system_id)]
                else:
                    self.systems[system_id].update_zone_data(zone_data)

                zone_id = int(zone_data.get(API_ZONE_ID, 0))
                if zone_id > 0:
                    system_zone_id = get_system_zone_id(system_id, zone_id)

                    if system_zone_id not in self.zones:
                        _zone = Zone(system_id, zone_id, zone_data)
                        self.zones[system_zone_id] = _zone
                        self.systems[system_id].add_zone(_zone)
                        self._new_zones += [system_zone_id]
                    else:
                        self.zones[system_zone_id].update_data(zone_data)

                    self.update_system_from_zone(
                        self.systems[system_id], self.zones[system_zone_id]
                    )

        self.update_zones_from_master_zone()

        if self._first_update:
            self._new_systems = []
            self._new_zones = []
        else:
            if len(self._new_systems) > 0:
                _LOGGER.debug("New systems detected: %s", self._new_systems)
            if len(self._new_zones) > 0:
                _LOGGER.debug("New zones detected: %s", self._new_zones)

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

    async def get_demo(self) -> dict[str, Any]:
        """Return Airzone demo."""
        res = await self.http_request(
            "POST",
            f"{API_V1}/{API_DEMO}",
        )
        self._api_raw_data[RAW_DEMO] = res
        return res

    async def get_dhw(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
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
        self._api_raw_data[RAW_DHW] = res
        return res

    async def get_hvac_systems(
        self, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
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
        self._api_raw_data[RAW_SYSTEMS] = res
        return res

    async def get_hvac(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
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
        self._api_raw_data[RAW_HVAC] = res
        return res

    async def get_integration(self) -> dict[str, Any]:
        """Return Airzone integration."""
        res = await self.http_request(
            "POST",
            f"{API_V1}/{API_INTEGRATION}",
        )
        self._api_raw_data[RAW_INTEGRATION] = res
        return res

    async def get_version(self) -> dict[str, Any]:
        """Return Airzone Local API version."""
        res = await self.http_request(
            "POST",
            f"{API_V1}/{API_VERSION}",
        )
        self._api_raw_data[RAW_VERSION] = res
        return res

    async def get_webserver(self) -> dict[str, Any]:
        """Return Airzone WebServer."""
        res = await self.http_request(
            "POST",
            f"{API_V1}/{API_WEBSERVER}",
        )
        self._api_raw_data[RAW_WEBSERVER] = res
        return res

    async def put_hvac(self, params: dict[str, Any]) -> dict[str, Any]:
        """Perform a PUT request to update HVAC parameters."""
        return await self.http_request(
            "PUT",
            f"{API_V1}/{API_HVAC}",
            params,
        )

    async def set_dhw_parameters(self, params: dict[str, Any]) -> dict[str, Any]:
        """Set Airzone Hot Water parameters and handle response."""
        res = await self.put_hvac(params)

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

    def new_systems(self) -> list[str]:
        """Return new systems detected in last update."""
        return self._new_systems

    def new_zones(self) -> list[str]:
        """Return new zones detected in last update."""
        return self._new_zones

    def raw_data(self) -> dict[str, Any]:
        """Return raw Airzone API data."""
        return self._api_raw_data

    def data(self) -> dict[str, Any]:
        """Return Airzone device data."""
        data: dict[str, Any] = {}

        if self.hotwater is not None:
            data[AZD_HOT_WATER] = self.hotwater.data()

        data[AZD_NEW_SYSTEMS] = self.new_systems()

        data[AZD_SYSTEMS_NUM] = self.num_systems()
        if len(self.systems) > 0:
            systems: dict[int, Any] = {}
            for system_id, system in self.systems.items():
                systems[system_id] = system.data()
            data[AZD_SYSTEMS] = systems

        if self.webserver is not None:
            data[AZD_WEBSERVER] = self.webserver.data()

        data[AZD_NEW_ZONES] = self.new_zones()

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
