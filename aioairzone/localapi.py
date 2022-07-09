"""Airzone Local API."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from enum import IntEnum
from json import JSONDecodeError
from typing import Any, cast

from aiohttp import ClientConnectorError, ClientSession
from aiohttp.client_reqrep import ClientResponse

from .const import (
    API_DATA,
    API_ERROR_METHOD_NOT_SUPPORTED,
    API_ERROR_REQUEST_MALFORMED,
    API_ERROR_SYSTEM_ID_NOT_AVAILABLE,
    API_ERROR_SYSTEM_ID_OUT_RANGE,
    API_ERROR_ZONE_ID_NOT_AVAILABLE,
    API_ERROR_ZONE_ID_NOT_PROVIDED,
    API_ERROR_ZONE_ID_OUT_RANGE,
    API_ERRORS,
    API_HVAC,
    API_MAC,
    API_SYSTEM_ID,
    API_SYSTEM_PARAMS,
    API_SYSTEMS,
    API_V1,
    API_WEBSERVER,
    API_ZONE_ID,
    API_ZONE_PARAMS,
    AZD_SYSTEMS,
    AZD_SYSTEMS_NUM,
    AZD_WEBSERVER,
    AZD_ZONES,
    AZD_ZONES_NUM,
    DEFAULT_PORT,
    DEFAULT_SYSTEM_ID,
    HTTP_CALL_TIMEOUT,
    RAW_HVAC,
    RAW_SYSTEMS,
    RAW_WEBSERVER,
)
from .device import System, Zone
from .exceptions import (
    APIError,
    InvalidHost,
    InvalidMethod,
    InvalidParam,
    InvalidSystem,
    InvalidZone,
    ParamUpdateFailure,
    RequestMalformed,
    SystemNotAvailable,
    SystemOutOfRange,
    ZoneNotAvailable,
    ZoneNotProvided,
    ZoneOutOfRange,
)
from .webserver import WebServer

_LOGGER = logging.getLogger(__name__)


class ApiFeature(IntEnum):
    """Supported features of the Airzone Local API."""

    HVAC = 0
    SYSTEMS = 1
    WEBSERVER = 2


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
        self.aiohttp_session = aiohttp_session
        self.api_features: int = ApiFeature.HVAC
        self.api_features_checked = False
        self.options = options
        self.systems: dict[int, System] = {}
        self.webserver: WebServer | None = None

    @staticmethod
    def handle_errors(errors: list[dict[str, str]]) -> None:
        """Handle API errors."""
        for error in errors:
            for key, val in error.items():
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
            raise InvalidHost from err

        try:
            resp_json = await resp.json(content_type=None)
        except JSONDecodeError as err:
            raise InvalidHost from err

        _LOGGER.debug("aiohttp response: %s", resp_json)
        if resp.status != 200:
            if API_ERRORS in resp_json:
                self.handle_errors(resp_json[API_ERRORS])
            raise APIError(f"HTTP status: {resp.status}")

        return cast(dict[str, Any], resp_json)

    def update_systems(self, data: dict[str, Any]) -> None:
        """Gather Systems data."""
        for api_system in data[API_SYSTEMS]:
            system = self.get_system(api_system[API_SYSTEM_ID])
            if system:
                system.update_data(api_system)

    def update_webserver(self, data: dict[str, Any]) -> None:
        """Gather WebServer data."""
        self.webserver = WebServer(data)

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

        self.api_features_checked = True

    async def update_features(self) -> None:
        """Gather Airzone features data."""
        if not self.api_features_checked:
            await self.check_features(True)
        else:
            if self.api_features & ApiFeature.SYSTEMS:
                self.update_systems(await self.get_hvac_systems())

            if self.api_features & ApiFeature.WEBSERVER:
                self.update_webserver(await self.get_webserver())

    async def validate(self) -> str | None:
        """Validate Airzone API."""
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

    async def update(self) -> bool:
        """Gather Airzone data."""
        systems: dict[int, System] = {}

        hvac = await self.get_hvac()
        if self.options.system_id == DEFAULT_SYSTEM_ID:
            for hvac_system in hvac[API_SYSTEMS]:
                system = System(hvac_system[API_DATA])
                if system and (_id := system.get_id()):
                    systems[_id] = system
        else:
            system = System(hvac[API_DATA])
            if system and (_id := system.get_id()):
                systems[_id] = system
        self.systems = systems

        await self.update_features()

        return bool(systems)

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

    async def set_hvac_parameters(self, params: dict[str, Any]) -> dict[str, Any]:
        """Set Airzone HVAC parameters and handle response."""
        res = await self.put_hvac(params)

        if API_DATA not in res:
            if API_ERRORS in res:
                self.handle_errors(res[API_ERRORS])
            raise APIError(f"set_hvac: {API_DATA} not in API response")

        data: dict[str, Any] = res[API_DATA][0]
        for key, value in params.items():
            if key not in data or data[key] != value:
                if key == API_SYSTEM_ID and value != 0:
                    raise InvalidSystem(
                        f"set_hvac: System mismatch: {data.get(key)} vs {value}"
                    )
                if key == API_ZONE_ID and value != 0:
                    raise InvalidZone(
                        f"set_hvac: Zone mismatch: {data.get(key)} vs {value}"
                    )
                if key not in data:
                    raise InvalidParam(f"set_hvac: param not in data: {key}={value}")
                raise ParamUpdateFailure(
                    f"set_hvac: param update failure: {key}={value}"
                )

        system = self.get_system(data[API_SYSTEM_ID])
        zone = self.get_zone(data[API_SYSTEM_ID], data[API_ZONE_ID])
        for key, value in data.items():
            if key in API_SYSTEM_PARAMS:
                system.set_param(key, value)
            elif key in API_ZONE_PARAMS:
                zone.set_param(key, value)

        return res

    def raw_data(self) -> dict[str, Any]:
        """Return raw Airzone API data."""
        return self._api_raw_data

    def data(self) -> dict[str, Any]:
        """Return Airzone device data."""
        data: dict[str, Any] = {
            AZD_SYSTEMS_NUM: self.num_systems(),
            AZD_ZONES_NUM: self.num_zones(),
        }

        if self.systems:
            systems: dict[int, Any] = {}
            zones: dict[str, Any] = {}
            for system_id, system in self.systems.items():
                systems[system_id] = system.data()
                for zone in system.zones.values():
                    zones[zone.get_system_zone_id()] = zone.data()
            data[AZD_SYSTEMS] = systems
            if self.webserver:
                data[AZD_WEBSERVER] = self.webserver.data()
            data[AZD_ZONES] = zones

        return data

    def get_system(self, system_id: int) -> System:
        """Return Airzone system."""
        for system in self.systems.values():
            if system.get_id() == system_id:
                return system
        raise InvalidSystem(f"System {system_id} not present")

    def get_zone(self, system_id: int, zone_id: int) -> Zone:
        """Return Airzone system zone."""
        return self.get_system(system_id).get_zone(zone_id)

    def num_systems(self) -> int:
        """Return number of airzone systems."""
        return len(self.systems)

    def num_zones(self) -> int:
        """Return total number of zones."""
        count = 0
        for system in self.systems.values():
            count += system.num_zones()
        return count
