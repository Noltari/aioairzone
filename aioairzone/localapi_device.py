"""Airzone Local API based device."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, cast

import aiohttp
from aiohttp.client_reqrep import ClientResponse

from .common import (
    AirzoneStages,
    AirzoneType,
    ConnectionOptions,
    OperationMode,
    TemperatureUnit,
)
from .const import (
    API_ACS_POINT,
    API_AIR_DEMAND,
    API_COLD_STAGE,
    API_COLD_STAGES,
    API_COOL_SET_POINT,
    API_DATA,
    API_ERROR_SYSTEM_ID_OUT_RANGE,
    API_ERROR_ZONE_ID_NOT_AVAILABLE,
    API_ERROR_ZONE_ID_OUT_RANGE,
    API_ERRORS,
    API_FLOOR_DEMAND,
    API_HEAT_STAGE,
    API_HEAT_STAGES,
    API_HUMIDITY,
    API_HVAC,
    API_MAX_TEMP,
    API_MIN_TEMP,
    API_MODE,
    API_MODES,
    API_NAME,
    API_ON,
    API_ROOM_TEMP,
    API_SET_POINT,
    API_SYSTEM_ID,
    API_SYSTEM_PARAMS,
    API_SYSTEMS,
    API_UNITS,
    API_V1,
    API_ZONE_ID,
    API_ZONE_PARAMS,
    AZD_AIR_DEMAND,
    AZD_COLD_STAGE,
    AZD_COLD_STAGES,
    AZD_DEMAND,
    AZD_ERRORS,
    AZD_FLOOR_DEMAND,
    AZD_HEAT_STAGE,
    AZD_HEAT_STAGES,
    AZD_HUMIDITY,
    AZD_ID,
    AZD_MODE,
    AZD_MODES,
    AZD_NAME,
    AZD_ON,
    AZD_PROBLEMS,
    AZD_SYSTEM,
    AZD_SYSTEMS,
    AZD_SYSTEMS_NUM,
    AZD_TEMP,
    AZD_TEMP_MAX,
    AZD_TEMP_MIN,
    AZD_TEMP_SET,
    AZD_TEMP_UNIT,
    AZD_TYPE,
    AZD_ZONES,
    AZD_ZONES_NUM,
    HTTP_CALL_TIMEOUT,
)
from .exceptions import (
    APIError,
    InvalidHost,
    InvalidParam,
    InvalidSystem,
    InvalidZone,
    ParamUpdateFailure,
)

_LOGGER = logging.getLogger(__name__)


class AirzoneLocalApi:
    """Airzone Local API device representation."""

    def __init__(
        self,
        aiohttp_session: aiohttp.ClientSession,
        options: ConnectionOptions,
    ):
        """Device init."""
        self.aiohttp_session: aiohttp.ClientSession = aiohttp_session
        self.options: ConnectionOptions = options
        self.connect_task = None
        self.connect_result = None
        self.systems: dict[int, System] = {}
        self._loop = asyncio.get_running_loop()

    @property
    def ip_address(self) -> str:
        """Device ip address."""
        return self.options.ip_address

    @property
    def port(self) -> int:
        """Device port."""
        return self.options.port

    async def http_request(
        self, method: str, path: str, data: Any | None = None
    ) -> dict[str, Any]:
        """Device HTTP request."""
        _LOGGER.debug("aiohttp request: /%s (params=%s)", path, data)
        resp: ClientResponse = await self.aiohttp_session.request(
            method,
            f"http://{self.options.ip_address}:{self.options.port}/{path}",
            data=json.dumps(data),
            raise_for_status=True,
            timeout=HTTP_CALL_TIMEOUT,
        )
        resp_json = await resp.json(content_type=None)
        _LOGGER.debug("aiohttp response: %s", resp_json)
        return cast(dict, resp_json)

    async def validate_airzone(self):
        """Gather Airzone systems."""
        response = await self.get_hvac()
        if API_SYSTEMS not in response:
            raise InvalidHost

    async def update_airzone(self) -> bool:
        """Gather Airzone systems."""
        systems = {}

        airzone_systems = await self.get_hvac()
        for airzone_system in airzone_systems[API_SYSTEMS]:
            system = System(self, airzone_system[API_DATA])
            if system:
                systems[system.get_id()] = system

        self.systems = systems

        return bool(systems)

    async def get_hvac(self, params: dict[str, Any] = None) -> dict[str, Any]:
        """Return Airzone HVAC."""
        if not params:
            params = {
                API_SYSTEM_ID: 0,
                API_ZONE_ID: 0,
            }
        res = await self.http_request(
            "POST",
            f"{API_V1}/{API_HVAC}",
            params,
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
                for error in res[API_ERRORS]:
                    if error == API_ERROR_SYSTEM_ID_OUT_RANGE:
                        raise InvalidSystem
                    if error == API_ERROR_ZONE_ID_OUT_RANGE:
                        raise InvalidZone
                    if error == API_ERROR_ZONE_ID_NOT_AVAILABLE:
                        raise InvalidZone
                    _LOGGER.error('HVAC PUT error: "%s"', error)
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

        system: System = self.get_system(data[API_SYSTEM_ID])
        zone: Zone = self.get_zone(data[API_SYSTEM_ID], data[API_ZONE_ID])
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
                for zone_id, zone in system.zones.items():
                    zones[f"{system_id}:{zone_id}"] = zone.data()
            data[AZD_SYSTEMS] = systems
            data[AZD_ZONES] = zones

        return data

    def get_system(self, system_id) -> System:
        """Return Airzone system."""
        system: System
        for system in self.systems.values():
            if system.get_id() == system_id:
                return system
        raise InvalidSystem

    def get_zone(self, system_id, zone_id) -> Zone:
        """Return Airzone system zone."""
        return self.get_system(system_id).get_zone(zone_id)

    def num_systems(self) -> int:
        """Return number of airzone systems."""
        if self.systems:
            return len(self.systems)
        return 0

    def num_zones(self) -> int:
        """Return total number of zones."""
        count = 0
        if self.systems:
            for system in self.systems.values():
                count += system.num_zones()
        return count


class System:
    """Airzone System."""

    def __init__(self, airzone, airzone_system):
        """System init."""
        self.airzone = airzone
        self.id = None
        self.master_zone = None
        self.type = None
        self.zones: dict[int, Zone] = {}

        for airzone_zone in airzone_system:
            zone = Zone(self, airzone_zone)
            if zone:
                _id = int(airzone_zone[API_SYSTEM_ID])
                if not self.id:
                    self.id = _id
                elif self.id != _id:
                    _LOGGER.error("System ID mismatch across zones")

                self.zones[zone.get_id()] = zone

                if zone.is_master():
                    self.master_zone = zone

                    if API_COOL_SET_POINT in airzone_zone:
                        self.type = AirzoneType.B
                    elif API_ACS_POINT in airzone_zone:
                        self.type = AirzoneType.A
                    else:
                        self.type = AirzoneType.C

    def data(self):
        """Return Airzone system data."""
        data = {
            AZD_ID: self.get_id(),
            AZD_ZONES_NUM: self.num_zones(),
        }

        if self.type:
            data[AZD_TYPE] = self.get_type()

        if self.zones:
            zones = {}
            for _id, zone in self.zones.items():
                zones[_id] = zone.data()
            data[AZD_ZONES] = zones

        return data

    def get_id(self) -> int:
        """Return system ID."""
        return self.id

    def get_master_zone(self) -> Zone:
        """Return Airzone master zone."""
        return self.master_zone

    def get_type(self) -> AirzoneType:
        """Return system type."""
        return self.type

    def get_zone(self, zone_id) -> Zone:
        """Return Airzone zone."""
        zone: Zone
        for zone in self.zones.values():
            if zone.get_id() == zone_id:
                return zone
        raise InvalidZone

    def num_zones(self) -> int:
        """Return number of system zones."""
        return len(self.zones)

    def set_param(self, key: str, value: Any) -> None:
        """Update zones parameters by key and value."""
        for zone in self.zones.values():
            zone.set_param(key, value)


class Zone:
    """Airzone Zone."""

    def __init__(self, system: System, zone):
        """Zone init."""
        self.air_demand = bool(zone[API_AIR_DEMAND])
        self.cold_stage = AirzoneStages(zone[API_COLD_STAGE])
        self.floor_demand = bool(zone[API_FLOOR_DEMAND])
        self.heat_stage = AirzoneStages(zone[API_HEAT_STAGE])
        self.humidity = int(zone[API_HUMIDITY])
        self.id = int(zone[API_ZONE_ID])
        self.master = None
        self.mode = OperationMode(zone[API_MODE])
        self.name = str(zone[API_NAME])
        self.on = bool(zone[API_ON])
        self.temp = float(zone[API_ROOM_TEMP])
        self.temp_max = float(zone[API_MAX_TEMP])
        self.temp_min = float(zone[API_MIN_TEMP])
        self.temp_set = float(zone[API_SET_POINT])
        self.temp_unit = TemperatureUnit(zone[API_UNITS])
        self.system = system

        if API_COLD_STAGES in zone:
            if isinstance(zone[API_COLD_STAGES], list):
                stages = []
                for stage in zone[API_COLD_STAGES]:
                    stages.append(AirzoneStages(stage))
                self.cold_stages = stages
            else:
                self.cold_stages = []
        else:
            self.cold_stages = []

        if len(zone[API_ERRORS]):
            self.errors = zone[API_ERRORS]
        else:
            self.errors = None

        if API_HEAT_STAGES in zone:
            if isinstance(zone[API_HEAT_STAGES], list):
                stages = []
                for stage in zone[API_HEAT_STAGES]:
                    stages.append(AirzoneStages(stage))
                self.heat_stages = stages
            else:
                self.heat_stages = []
        else:
            self.heat_stages = []

        if API_MODES in zone:
            modes = []
            for mode in zone[API_MODES]:
                modes.append(OperationMode(mode))
            self.modes = modes
        else:
            self.modes = []

    def data(self):
        """Return Airzone zone data."""
        data = {
            AZD_AIR_DEMAND: self.get_air_demand(),
            AZD_COLD_STAGE: self.get_cold_stage(),
            AZD_DEMAND: self.get_demand(),
            AZD_FLOOR_DEMAND: self.get_floor_demand(),
            AZD_HEAT_STAGE: self.get_heat_stage(),
            AZD_HUMIDITY: self.get_humidity(),
            AZD_ID: self.get_id(),
            AZD_MODE: self.get_mode(),
            AZD_NAME: self.get_name(),
            AZD_ON: self.get_on(),
            AZD_PROBLEMS: self.get_problems(),
            AZD_SYSTEM: self.get_system_id(),
            AZD_TEMP: self.get_temp(),
            AZD_TEMP_MAX: self.get_temp_max(),
            AZD_TEMP_MIN: self.get_temp_min(),
            AZD_TEMP_SET: self.get_temp_set(),
            AZD_TEMP_UNIT: self.get_temp_unit(),
        }

        if self.cold_stages:
            data[AZD_COLD_STAGES] = self.get_cold_stages()

        if self.errors:
            data[AZD_ERRORS] = self.get_errors()

        if self.heat_stages:
            data[AZD_HEAT_STAGES] = self.get_heat_stages()

        if self.modes:
            data[AZD_MODES] = self.get_modes()

        return data

    def get_air_demand(self) -> bool:
        """Return zone air demand."""
        return self.air_demand

    def get_cold_stage(self) -> AirzoneStages:
        """Return zone cold stage."""
        return self.cold_stage

    def get_cold_stages(self) -> list[AirzoneStages]:
        """Return zone cold stages."""
        return self.cold_stages

    def get_demand(self) -> bool:
        """Return zone demand."""
        return self.get_air_demand() or self.get_floor_demand()

    def get_errors(self) -> list:
        """Return zone errors."""
        return self.errors

    def get_floor_demand(self) -> bool:
        """Return zone floor demand."""
        return self.floor_demand

    def get_id(self) -> int:
        """Return zone ID."""
        return self.id

    def get_heat_stage(self) -> AirzoneStages:
        """Return zone heat stage."""
        return self.heat_stage

    def get_heat_stages(self) -> list[AirzoneStages]:
        """Return zone heat stages."""
        return self.heat_stages

    def get_humidity(self) -> int:
        """Return zone humidity."""
        return self.humidity

    def get_mode(self) -> OperationMode:
        """Return zone mode."""
        return self.mode

    def get_modes(self) -> list[OperationMode]:
        """Return zone modes."""
        return self.modes

    def get_name(self) -> str:
        """Return zone name."""
        return self.name

    def get_on(self) -> bool:
        """Return zone on/off."""
        return self.on

    def get_problems(self) -> bool:
        """Return zone problems."""
        return bool(self.errors)

    def get_system_id(self) -> int:
        """Return system ID."""
        return self.system.get_id()

    def get_temp(self) -> float:
        """Return zone temperature."""
        return round(self.temp, 2)

    def get_temp_max(self) -> float:
        """Return zone maximum temperature."""
        return round(self.temp_max, 1)

    def get_temp_min(self) -> float:
        """Return zone minimum temperature."""
        return round(self.temp_min, 1)

    def get_temp_set(self) -> float:
        """Return zone set temperature."""
        return round(self.temp_set, 1)

    def get_temp_unit(self) -> TemperatureUnit:
        """Return zone temperature unit."""
        return self.temp_unit

    def is_master(self) -> bool:
        """Zone is master if mode can be changed."""
        return self.modes is not None

    def set_param(self, key: str, value: Any) -> None:
        """Update zone parameter by key and value."""
        if key == API_COLD_STAGE:
            self.cold_stage = value
        elif key == API_HEAT_STAGE:
            self.heat_stage = value
        elif key == API_MODE:
            self.mode = value
        elif key == API_NAME:
            self.name = value
        elif key == API_ON:
            self.on = value
        elif key == API_SET_POINT:
            self.temp_set = value
