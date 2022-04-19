"""Airzone Local API."""
from __future__ import annotations

import json
import logging
from typing import Any, cast

from aiohttp import ClientSession
from aiohttp.client_reqrep import ClientResponse

from .common import ConnectionOptions
from .const import (
    API_DATA,
    API_ERROR_METHOD_NOT_SUPPORTED,
    API_ERROR_SYSTEM_ID_NOT_AVAILABLE,
    API_ERROR_SYSTEM_ID_OUT_RANGE,
    API_ERROR_ZONE_ID_NOT_AVAILABLE,
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
    HTTP_CALL_TIMEOUT,
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
    SystemNotAvailable,
    SystemOutOfRange,
)
from .webserver import WebServer

_LOGGER = logging.getLogger(__name__)


class AirzoneLocalApi:
    """Airzone Local API device representation."""

    def __init__(
        self,
        aiohttp_session: ClientSession,
        options: ConnectionOptions,
    ):
        """Device init."""
        self.aiohttp_session = aiohttp_session
        self.options = options
        self.supports_systems: bool = False
        self.supports_webserver: bool = False
        self.systems: dict[int, System] = {}
        self.webserver: WebServer | None = None

    @staticmethod
    def handle_errors(errors: list[dict[str, str]]) -> None:
        """Handle API errors."""
        for error in errors:
            for val in error.values():
                if val == API_ERROR_SYSTEM_ID_NOT_AVAILABLE:
                    raise SystemNotAvailable
                if val == API_ERROR_SYSTEM_ID_OUT_RANGE:
                    raise SystemOutOfRange
                if val == API_ERROR_METHOD_NOT_SUPPORTED:
                    raise InvalidMethod
                if val == API_ERROR_ZONE_ID_OUT_RANGE:
                    raise InvalidZone
                if val == API_ERROR_ZONE_ID_NOT_AVAILABLE:
                    raise InvalidZone
                _LOGGER.error('API error: "%s"', error)

    async def http_request(
        self, method: str, path: str, data: Any | None = None
    ) -> dict[str, Any]:
        """Device HTTP request."""
        _LOGGER.debug("aiohttp request: /%s (params=%s)", path, data)
        resp: ClientResponse = await self.aiohttp_session.request(
            method,
            f"http://{self.options.host}:{self.options.port}/{path}",
            data=json.dumps(data),
            timeout=HTTP_CALL_TIMEOUT,
        )
        resp_json = await resp.json(content_type=None)
        _LOGGER.debug("aiohttp response: %s", resp_json)
        if resp.status != 200:
            if API_ERRORS in resp_json:
                self.handle_errors(resp_json[API_ERRORS])
            raise APIError
        return cast(dict, resp_json)

    async def validate(self) -> str | None:
        """Validate Airzone API."""
        airzone_mac: str | None = None

        try:
            response = await self.get_webserver()
            self.supports_webserver = bool(API_MAC in response)
            if self.supports_webserver:
                airzone_mac = str(response[API_MAC])
        except InvalidMethod:
            self.supports_webserver = False

        try:
            response = await self.get_hvac_systems()
            self.supports_systems = bool(API_SYSTEMS in response)
        except SystemOutOfRange:
            self.supports_systems = False

        response = await self.get_hvac()
        if self.options.system_id == 0:
            if API_SYSTEMS not in response:
                raise InvalidHost
        elif API_DATA not in response:
            raise InvalidHost

        return airzone_mac

    async def update(self) -> bool:
        """Gather Airzone data."""
        systems: dict[int, System] = {}

        hvac = await self.get_hvac()
        if self.options.system_id == 0:
            for hvac_system in hvac[API_SYSTEMS]:
                system = System(hvac_system[API_DATA])
                if system:
                    systems[system.get_id()] = system
        else:
            system = System(hvac[API_DATA])
            if system:
                systems[system.get_id()] = system

        self.systems = systems

        if self.supports_systems:
            api_systems = await self.get_hvac_systems()
            for api_system in api_systems[API_SYSTEMS]:
                system = self.get_system(api_system[API_SYSTEM_ID])
                if system:
                    system.update_data(api_system)

        if self.supports_webserver:
            webserver_data = await self.get_webserver()
            self.webserver = WebServer(webserver_data)

        return bool(systems)

    async def get_hvac_systems(self, params: dict[str, Any] = None) -> dict[str, Any]:
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
        return res

    async def get_hvac(self, params: dict[str, Any] = None) -> dict[str, Any]:
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
        return res

    async def get_webserver(self) -> dict[str, Any]:
        """Return Airzone WebServer."""
        res = await self.http_request(
            "POST",
            f"{API_V1}/{API_WEBSERVER}",
        )
        return res

    async def put_hvac(self, params: dict[str, Any]) -> dict[str, Any]:
        """Return Airzone HVAC."""
        res = await self.http_request(
            "PUT",
            f"{API_V1}/{API_HVAC}",
            params,
        )

        if API_DATA not in res:
            if API_ERRORS in res:
                self.handle_errors(res[API_ERRORS])
            raise APIError

        data: dict = res[API_DATA][0]
        for key, value in params.items():
            if key not in data or data[key] != value:
                if key == API_SYSTEM_ID and value != 0:
                    raise InvalidSystem
                if key == API_ZONE_ID and value != 0:
                    raise InvalidZone
                if key not in data:
                    raise InvalidParam
                raise ParamUpdateFailure

        system = self.get_system(data[API_SYSTEM_ID])
        zone = self.get_zone(data[API_SYSTEM_ID], data[API_ZONE_ID])
        for key, value in data.items():
            if key in API_SYSTEM_PARAMS:
                system.set_param(key, value)
            elif key in API_ZONE_PARAMS:
                zone.set_param(key, value)

        return res

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
        raise InvalidSystem

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
