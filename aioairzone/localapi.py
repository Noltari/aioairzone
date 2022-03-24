"""Airzone Local API based device."""
from __future__ import annotations

import json
import logging
from typing import Any, cast

from aiohttp import ClientSession
from aiohttp.client_reqrep import ClientResponse

from .common import (
    AirzoneStages,
    ConnectionOptions,
    OperationMode,
    TemperatureUnit,
    ThermostatType,
)
from .const import (
    API_AIR_DEMAND,
    API_COLD_STAGE,
    API_COLD_STAGES,
    API_COOL_MAX_TEMP,
    API_COOL_MIN_TEMP,
    API_COOL_SET_POINT,
    API_DATA,
    API_ERROR_SYSTEM_ID_OUT_RANGE,
    API_ERROR_ZONE_ID_NOT_AVAILABLE,
    API_ERROR_ZONE_ID_OUT_RANGE,
    API_ERRORS,
    API_FLOOR_DEMAND,
    API_HEAT_MAX_TEMP,
    API_HEAT_MIN_TEMP,
    API_HEAT_SET_POINT,
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
    API_THERMOS_FIRMWARE,
    API_THERMOS_RADIO,
    API_THERMOS_TYPE,
    API_UNITS,
    API_V1,
    API_ZONE_ID,
    API_ZONE_PARAMS,
    AZD_AIR_DEMAND,
    AZD_COLD_STAGE,
    AZD_COLD_STAGES,
    AZD_COOL_TEMP_MAX,
    AZD_COOL_TEMP_MIN,
    AZD_COOL_TEMP_SET,
    AZD_DEMAND,
    AZD_ERRORS,
    AZD_FLOOR_DEMAND,
    AZD_HEAT_STAGE,
    AZD_HEAT_STAGES,
    AZD_HEAT_TEMP_MAX,
    AZD_HEAT_TEMP_MIN,
    AZD_HEAT_TEMP_SET,
    AZD_HUMIDITY,
    AZD_ID,
    AZD_MASTER,
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
    AZD_THERMOSTAT_FW,
    AZD_THERMOSTAT_MODEL,
    AZD_THERMOSTAT_RADIO,
    AZD_ZONES,
    AZD_ZONES_NUM,
    HTTP_CALL_TIMEOUT,
    THERMOSTAT_RADIO,
    THERMOSTAT_WIRED,
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
        aiohttp_session: ClientSession,
        options: ConnectionOptions,
    ):
        """Device init."""
        self.aiohttp_session = aiohttp_session
        self.options = options
        self.systems: dict[int, System] = {}

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

    async def validate_airzone(self) -> None:
        """Gather Airzone systems."""
        response = await self.get_hvac()
        if API_SYSTEMS not in response:
            raise InvalidHost

    async def update_airzone(self) -> bool:
        """Gather Airzone systems."""
        systems: dict[int, System] = {}

        airzone_systems = await self.get_hvac()
        for airzone_system in airzone_systems[API_SYSTEMS]:
            system = System(airzone_system[API_DATA])
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


class System:
    """Airzone System."""

    def __init__(self, airzone_system):
        """System init."""
        self.id = None
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

    def data(self) -> dict[str, Any]:
        """Return Airzone system data."""
        data: dict[str, Any] = {
            AZD_ID: self.get_id(),
            AZD_ZONES_NUM: self.num_zones(),
        }

        if self.zones:
            zones: dict[int, Any] = {}
            for _id, zone in self.zones.items():
                zones[_id] = zone.data()
            data[AZD_ZONES] = zones

        return data

    def get_id(self) -> int:
        """Return system ID."""
        return self.id

    def get_zone(self, zone_id: int) -> Zone:
        """Return Airzone zone."""
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


class Thermostat:
    """Airzone Thermostat."""

    def __init__(self, data: dict[str, Any]):
        self.firmware: str | None = None
        self.radio: bool | None = None
        self.type: ThermostatType | None = None

        if API_THERMOS_FIRMWARE in data:
            self.firmware = str(data[API_THERMOS_FIRMWARE])
        if API_THERMOS_RADIO in data:
            self.radio = bool(data[API_THERMOS_RADIO])
        if API_THERMOS_TYPE in data:
            self.type = ThermostatType(data[API_THERMOS_TYPE])

    def get_firmware(self) -> str | None:
        """Return Airzone Thermostat firmware."""
        if self.firmware and "." not in self.firmware and len(self.firmware) > 2:
            return f"{self.firmware[0:1]}.{self.firmware[1:]}"
        return self.firmware

    def get_model(self) -> str | None:
        """Return Airzone Thermostat model."""
        if self.type:
            name = str(self.type)
            sfx = THERMOSTAT_RADIO if self.radio else THERMOSTAT_WIRED
            return f"{name} ({sfx})"
        return None

    def get_radio(self) -> bool | None:
        """Return Airzone Thermostat radio."""
        return self.radio


class Zone:
    """Airzone Zone."""

    def __init__(self, system: System, zone: dict[str, Any]):
        """Zone init."""
        self.air_demand = bool(zone[API_AIR_DEMAND])
        self.cold_stage = AirzoneStages(zone[API_COLD_STAGE])
        self.cold_stages: list[AirzoneStages] = []
        self.cool_temp_max: float | None = None
        self.cool_temp_min: float | None = None
        self.cool_temp_set: float | None = None
        self.errors: list | None = None
        self.floor_demand = bool(zone[API_FLOOR_DEMAND])
        self.heat_temp_max: float | None = None
        self.heat_temp_min: float | None = None
        self.heat_temp_set: float | None = None
        self.heat_stage = AirzoneStages(zone[API_HEAT_STAGE])
        self.heat_stages: list[AirzoneStages] = []
        self.humidity = int(zone[API_HUMIDITY])
        self.id = int(zone[API_ZONE_ID])
        self.master = bool(API_MODES in zone)
        self.mode = OperationMode(zone[API_MODE])
        self.modes: list[OperationMode] = []
        self.name = str(zone[API_NAME])
        self.on = bool(zone[API_ON])
        self.temp = float(zone[API_ROOM_TEMP])
        self.temp_max = float(zone[API_MAX_TEMP])
        self.temp_min = float(zone[API_MIN_TEMP])
        self.temp_set = float(zone[API_SET_POINT])
        self.temp_unit = TemperatureUnit(zone[API_UNITS])
        self.thermostat = Thermostat(zone)
        self.system = system

        if API_COLD_STAGES in zone:
            cold_stages = AirzoneStages(zone[API_COLD_STAGES])
            self.cold_stages = cold_stages.to_list()
        elif self.cold_stage:
            self.cold_stages = [self.cold_stage]
        if API_HEAT_STAGES in zone:
            heat_stages = AirzoneStages(zone[API_HEAT_STAGES])
            self.heat_stages = heat_stages.to_list()
        elif self.heat_stage:
            self.heat_stages = [self.heat_stage]

        if API_COOL_MAX_TEMP in zone:
            self.cool_temp_max = float(zone[API_COOL_MAX_TEMP])
        if API_COOL_MIN_TEMP in zone:
            self.cool_temp_min = float(zone[API_COOL_MIN_TEMP])
        if API_COOL_SET_POINT in zone:
            self.cool_temp_set = float(zone[API_COOL_SET_POINT])
        if API_HEAT_MAX_TEMP in zone:
            self.heat_temp_max = float(zone[API_HEAT_MAX_TEMP])
        if API_HEAT_MIN_TEMP in zone:
            self.heat_temp_min = float(zone[API_HEAT_MIN_TEMP])
        if API_HEAT_SET_POINT in zone:
            self.heat_temp_set = float(zone[API_HEAT_SET_POINT])

        if len(zone[API_ERRORS]):
            self.errors = zone[API_ERRORS]

        if self.master:
            for mode in zone[API_MODES]:
                self.modes.append(OperationMode(mode))
        else:
            self.modes.append(self.mode)
        if OperationMode.STOP not in self.modes:
            self.modes.append(OperationMode.STOP)

    def data(self) -> dict[str, Any]:
        """Return Airzone zone data."""
        data = {
            AZD_AIR_DEMAND: self.get_air_demand(),
            AZD_COLD_STAGE: self.get_cold_stage(),
            AZD_DEMAND: self.get_demand(),
            AZD_FLOOR_DEMAND: self.get_floor_demand(),
            AZD_HEAT_STAGE: self.get_heat_stage(),
            AZD_HUMIDITY: self.get_humidity(),
            AZD_ID: self.get_id(),
            AZD_MASTER: self.get_master(),
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

        if self.cool_temp_max:
            data[AZD_COOL_TEMP_MAX] = self.get_cool_temp_max()
        if self.cool_temp_min:
            data[AZD_COOL_TEMP_MIN] = self.get_cool_temp_min()
        if self.cool_temp_set:
            data[AZD_COOL_TEMP_SET] = self.get_cool_temp_set()
        if self.heat_temp_max:
            data[AZD_HEAT_TEMP_MAX] = self.get_heat_temp_max()
        if self.heat_temp_min:
            data[AZD_HEAT_TEMP_MIN] = self.get_heat_temp_min()
        if self.heat_temp_set:
            data[AZD_HEAT_TEMP_SET] = self.get_heat_temp_set()

        if self.cold_stages:
            data[AZD_COLD_STAGES] = self.get_cold_stages()
        if self.heat_stages:
            data[AZD_HEAT_STAGES] = self.get_heat_stages()

        if self.errors:
            data[AZD_ERRORS] = self.get_errors()

        if self.modes:
            data[AZD_MODES] = self.get_modes()

        if self.thermostat.firmware:
            data[AZD_THERMOSTAT_FW] = self.thermostat.get_firmware()
        if self.thermostat.type:
            data[AZD_THERMOSTAT_MODEL] = self.thermostat.get_model()
        if self.thermostat.radio:
            data[AZD_THERMOSTAT_RADIO] = self.thermostat.get_radio()

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

    def get_cool_temp_max(self) -> float | None:
        """Return zone maximum cool temperature."""
        if self.cool_temp_max:
            return round(self.cool_temp_max, 1)
        return None

    def get_cool_temp_min(self) -> float | None:
        """Return zone minimum cool temperature."""
        if self.cool_temp_min:
            return round(self.cool_temp_min, 1)
        return None

    def get_cool_temp_set(self) -> float | None:
        """Return zone set cool temperature."""
        if self.cool_temp_set:
            return round(self.cool_temp_set, 1)
        return None

    def get_demand(self) -> bool:
        """Return zone demand."""
        return self.get_air_demand() or self.get_floor_demand()

    def get_heat_temp_max(self) -> float | None:
        """Return zone maximum heat temperature."""
        if self.heat_temp_max:
            return round(self.heat_temp_max, 1)
        return None

    def get_heat_temp_min(self) -> float | None:
        """Return zone minimum heat temperature."""
        if self.heat_temp_min:
            return round(self.heat_temp_min, 1)
        return None

    def get_heat_temp_set(self) -> float | None:
        """Return zone set heat temperature."""
        if self.heat_temp_set:
            return round(self.heat_temp_set, 1)
        return None

    def get_errors(self) -> list | None:
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

    def get_master(self) -> bool:
        """Return zone master/slave."""
        return self.master

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

    def get_system_zone_id(self) -> str:
        """Combine System and Zone IDs into a single ID."""
        return f"{self.get_system_id()}:{self.get_id()}"

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

    def set_param(self, key: str, value: Any) -> None:
        """Update zone parameter by key and value."""
        if key == API_COOL_SET_POINT:
            self.cool_temp_set = float(value)
        elif key == API_COLD_STAGE:
            self.cold_stage = AirzoneStages(value)
        elif key == API_HEAT_SET_POINT:
            self.heat_temp_set = float(value)
        elif key == API_HEAT_STAGE:
            self.heat_stage = AirzoneStages(value)
        elif key == API_MODE:
            self.mode = OperationMode(value)
        elif key == API_NAME:
            self.name = str(value)
        elif key == API_ON:
            self.on = bool(value)
        elif key == API_SET_POINT:
            self.temp_set = float(value)
