"""Airzone Local API Device."""
from __future__ import annotations

import logging
from typing import Any

from .common import (
    AirzoneStages,
    OperationMode,
    SystemType,
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
    API_DOUBLE_SET_POINT,
    API_DOUBLE_SET_POINT_PARAMS,
    API_ERROR_LOW_BATTERY,
    API_ERRORS,
    API_FLOOR_DEMAND,
    API_HEAT_MAX_TEMP,
    API_HEAT_MIN_TEMP,
    API_HEAT_SET_POINT,
    API_HEAT_STAGE,
    API_HEAT_STAGES,
    API_HUMIDITY,
    API_MAX_TEMP,
    API_MIN_TEMP,
    API_MODE,
    API_MODES,
    API_NAME,
    API_ON,
    API_POWER,
    API_ROOM_TEMP,
    API_SET_POINT,
    API_SPEED,
    API_SPEEDS,
    API_SYSTEM_FIRMWARE,
    API_SYSTEM_ID,
    API_SYSTEM_TYPE,
    API_THERMOS_FIRMWARE,
    API_THERMOS_RADIO,
    API_THERMOS_TYPE,
    API_UNITS,
    API_ZONE_ID,
    AZD_AIR_DEMAND,
    AZD_BATTERY_LOW,
    AZD_COLD_STAGE,
    AZD_COLD_STAGES,
    AZD_COOL_TEMP_MAX,
    AZD_COOL_TEMP_MIN,
    AZD_COOL_TEMP_SET,
    AZD_DEMAND,
    AZD_DOUBLE_SET_POINT,
    AZD_ERRORS,
    AZD_FIRMWARE,
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
    AZD_MODEL,
    AZD_MODES,
    AZD_NAME,
    AZD_ON,
    AZD_POWER,
    AZD_PROBLEMS,
    AZD_SPEED,
    AZD_SPEEDS,
    AZD_SYSTEM,
    AZD_TEMP,
    AZD_TEMP_MAX,
    AZD_TEMP_MIN,
    AZD_TEMP_SET,
    AZD_TEMP_UNIT,
    AZD_THERMOSTAT_FW,
    AZD_THERMOSTAT_MODEL,
    AZD_THERMOSTAT_RADIO,
    AZD_ZONES_NUM,
    ERROR_SYSTEM,
    ERROR_ZONE,
    THERMOSTAT_RADIO,
    THERMOSTAT_WIRED,
)
from .exceptions import InvalidZone

_LOGGER = logging.getLogger(__name__)


class System:
    """Airzone System."""

    def __init__(self, airzone_system):
        """System init."""
        self.errors: list[str] = []
        self.id = None
        self.firmware: str | None = None
        self.modes: list[OperationMode] = []
        self.power: bool | None = None
        self.type: SystemType | None = None
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
            AZD_PROBLEMS: self.get_problems(),
            AZD_ZONES_NUM: self.num_zones(),
        }

        errors = self.get_errors()
        if len(errors) > 0:
            data[AZD_ERRORS] = errors

        if self.firmware is not None:
            data[AZD_FIRMWARE] = self.get_firmware()

        if self.type is not None:
            data[AZD_MODEL] = self.get_model()

        if self.power is not None:
            data[AZD_POWER] = self.get_power()

        return data

    def add_error(self, val: str) -> None:
        """Add system error."""
        if val not in self.errors:
            self.errors.append(val)

    def get_errors(self) -> list[str]:
        """Return system errors."""
        return self.errors

    def get_id(self) -> int:
        """Return system ID."""
        return self.id

    def get_firmware(self) -> str | None:
        """Return system firmware."""
        if self.firmware and "." not in self.firmware and len(self.firmware) > 2:
            return f"{self.firmware[0:1]}.{self.firmware[1:]}"
        return self.firmware

    def get_model(self) -> str | None:
        """Return system model."""
        if self.type:
            return str(self.type)
        return None

    def get_modes(self) -> list[OperationMode]:
        """Return system modes."""
        return self.modes

    def get_power(self) -> bool | None:
        """Return system power."""
        return self.power

    def get_problems(self) -> bool:
        """Return system problems."""
        return bool(self.errors)

    def get_zone(self, zone_id: int) -> Zone:
        """Return Airzone zone."""
        for zone in self.zones.values():
            if zone.get_id() == zone_id:
                return zone
        raise InvalidZone

    def num_zones(self) -> int:
        """Return number of system zones."""
        return len(self.zones)

    def set_modes(self, modes: list[OperationMode]) -> None:
        """Set system modes."""
        self.modes = modes

    def set_param(self, key: str, value: Any) -> None:
        """Update zones parameters by key and value."""
        for zone in self.zones.values():
            zone.set_param(key, value)

    def update_data(self, data: dict[str, Any]) -> None:
        """Update system parameters by dict."""
        if API_SYSTEM_FIRMWARE in data:
            self.firmware = str(data[API_SYSTEM_FIRMWARE])

        if API_POWER in data:
            self.power = bool(data[API_POWER])

        if API_SYSTEM_TYPE in data:
            self.type = SystemType(data[API_SYSTEM_TYPE])


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
            if self.type.exists_radio():
                sfx = f" ({THERMOSTAT_RADIO if self.radio else THERMOSTAT_WIRED})"
            else:
                sfx = ""
            return f"{name}{sfx}"
        return None

    def get_radio(self) -> bool | None:
        """Return Airzone Thermostat radio."""
        return self.radio


class Zone:
    """Airzone Zone."""

    def __init__(self, system: System, zone: dict[str, Any]):
        """Zone init."""
        self.air_demand = bool(zone[API_AIR_DEMAND])
        self.cold_stage: AirzoneStages | None = None
        self.cold_stages: list[AirzoneStages] = []
        self.cool_temp_max: float | None = None
        self.cool_temp_min: float | None = None
        self.cool_temp_set: float | None = None
        self.double_set_point: bool = False
        self.errors: list[str] = []
        self.floor_demand = bool(zone[API_FLOOR_DEMAND])
        self.heat_temp_max: float | None = None
        self.heat_temp_min: float | None = None
        self.heat_temp_set: float | None = None
        self.heat_stage: AirzoneStages | None = None
        self.heat_stages: list[AirzoneStages] = []
        self.humidity: int | None = None
        self.id = int(zone[API_ZONE_ID])
        self.master = bool(API_MODES in zone)
        self.mode = OperationMode(zone[API_MODE])
        self.modes: list[OperationMode] = []
        self.name = str(zone[API_NAME])
        self.on = bool(zone[API_ON])
        self.speed: int | None = None
        self.speeds: int | None = None
        self.temp = float(zone[API_ROOM_TEMP])
        self.temp_max = float(zone[API_MAX_TEMP])
        self.temp_min = float(zone[API_MIN_TEMP])
        self.temp_set = float(zone[API_SET_POINT])
        self.temp_unit = TemperatureUnit(zone[API_UNITS])
        self.thermostat = Thermostat(zone)
        self.system = system

        if API_HUMIDITY in zone:
            self.humidity = int(zone[API_HUMIDITY])

        if API_COLD_STAGE in zone:
            self.cold_stage = AirzoneStages(zone[API_COLD_STAGE])
        if API_COLD_STAGES in zone:
            cold_stages = AirzoneStages(zone[API_COLD_STAGES])
            self.cold_stages = cold_stages.to_list()
        elif self.cold_stage and self.cold_stage.exists():
            self.cold_stages = [self.cold_stage]

        if API_HEAT_STAGE in zone:
            self.heat_stage = AirzoneStages(zone[API_HEAT_STAGE])
        if API_HEAT_STAGES in zone:
            heat_stages = AirzoneStages(zone[API_HEAT_STAGES])
            self.heat_stages = heat_stages.to_list()
        elif self.heat_stage and self.heat_stage.exists():
            self.heat_stages = [self.heat_stage]

        if API_COOL_MAX_TEMP in zone:
            self.cool_temp_max = float(zone[API_COOL_MAX_TEMP])
        if API_COOL_MIN_TEMP in zone:
            self.cool_temp_min = float(zone[API_COOL_MIN_TEMP])
        if API_COOL_SET_POINT in zone:
            self.cool_temp_set = float(zone[API_COOL_SET_POINT])
        if API_DOUBLE_SET_POINT in zone:
            self.double_set_point = bool(zone[API_DOUBLE_SET_POINT])
        else:
            self.double_set_point = zone.keys() >= API_DOUBLE_SET_POINT_PARAMS
        if API_HEAT_MAX_TEMP in zone:
            self.heat_temp_max = float(zone[API_HEAT_MAX_TEMP])
        if API_HEAT_MIN_TEMP in zone:
            self.heat_temp_min = float(zone[API_HEAT_MIN_TEMP])
        if API_HEAT_SET_POINT in zone:
            self.heat_temp_set = float(zone[API_HEAT_SET_POINT])

        if API_ERRORS in zone:
            errors: list[dict[str, str]] = zone[API_ERRORS]
            for error in errors:
                for key, val in error.items():
                    self.add_error(key, val)

        if API_SPEED in zone:
            self.speed = int(zone[API_SPEED])
        if API_SPEEDS in zone:
            self.speeds = int(zone[API_SPEEDS])

        if self.master:
            for mode in zone[API_MODES]:
                self.modes.append(OperationMode(mode))
            if OperationMode.STOP not in self.modes:
                self.modes.append(OperationMode.STOP)
            self.system.set_modes(self.modes)

    def data(self) -> dict[str, Any]:
        """Return Airzone zone data."""
        data = {
            AZD_AIR_DEMAND: self.get_air_demand(),
            AZD_DEMAND: self.get_demand(),
            AZD_DOUBLE_SET_POINT: self.get_double_set_point(),
            AZD_FLOOR_DEMAND: self.get_floor_demand(),
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

        humidity = self.get_humidity()
        if humidity is not None:
            data[AZD_HUMIDITY] = humidity

        if data[AZD_DOUBLE_SET_POINT]:
            cool_temp_max = self.get_cool_temp_max()
            if cool_temp_max:
                data[AZD_COOL_TEMP_MAX] = cool_temp_max
            cool_temp_min = self.get_cool_temp_min()
            if cool_temp_min:
                data[AZD_COOL_TEMP_MIN] = cool_temp_min
            cool_temp_set = self.get_cool_temp_set()
            if cool_temp_set:
                data[AZD_COOL_TEMP_SET] = cool_temp_set
            heat_temp_max = self.get_heat_temp_max()
            if heat_temp_max:
                data[AZD_HEAT_TEMP_MAX] = heat_temp_max
            heat_temp_min = self.get_heat_temp_min()
            if heat_temp_min:
                data[AZD_HEAT_TEMP_MIN] = heat_temp_min
            heat_temp_set = self.get_heat_temp_set()
            if heat_temp_set:
                data[AZD_HEAT_TEMP_SET] = heat_temp_set

        cold_stage = self.get_cold_stage()
        if cold_stage is not None:
            data[AZD_COLD_STAGE] = cold_stage
        cold_stages = self.get_cold_stages()
        if cold_stages is not None:
            data[AZD_COLD_STAGES] = cold_stages

        heat_stage = self.get_heat_stage()
        if heat_stage is not None:
            data[AZD_HEAT_STAGE] = heat_stage
        heat_stages = self.get_heat_stages()
        if heat_stages is not None:
            data[AZD_HEAT_STAGES] = heat_stages

        speed = self.get_speed()
        if speed is not None:
            data[AZD_SPEED] = speed
        speeds = self.get_speeds()
        if speeds is not None:
            data[AZD_SPEEDS] = speeds

        errors = self.get_errors()
        if len(errors) > 0:
            data[AZD_ERRORS] = errors

        modes = self.get_modes()
        if modes is not None:
            data[AZD_MODES] = modes

        thermostat_firmware = self.thermostat.get_firmware()
        if thermostat_firmware is not None:
            data[AZD_THERMOSTAT_FW] = thermostat_firmware
        thermostat_model = self.thermostat.get_model()
        if thermostat_model is not None:
            data[AZD_THERMOSTAT_MODEL] = thermostat_model
        thermostat_radio = self.thermostat.get_radio()
        if thermostat_radio is not None:
            data[AZD_THERMOSTAT_RADIO] = thermostat_radio

        battery_low = self.get_battery_low()
        if battery_low is not None:
            data[AZD_BATTERY_LOW] = battery_low

        return data

    def add_error(self, key: str, val: str) -> None:
        """Add system or zone error."""
        _key = key.casefold()
        if _key == ERROR_SYSTEM:
            self.system.add_error(val)
        elif _key == ERROR_ZONE:
            if val not in self.errors:
                self.errors.append(val)

    def get_air_demand(self) -> bool:
        """Return zone air demand."""
        return self.air_demand

    def get_battery_low(self) -> bool | None:
        """Return battery status."""
        if self.thermostat.get_radio():
            return API_ERROR_LOW_BATTERY in self.errors
        return None

    def get_cold_stage(self) -> AirzoneStages | None:
        """Return zone cold stage."""
        return self.cold_stage

    def get_cold_stages(self) -> list[AirzoneStages] | None:
        """Return zone cold stages."""
        if len(self.cold_stages) > 0:
            return self.cold_stages
        return None

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

    def get_double_set_point(self) -> bool:
        """Return zone double set point."""
        return self.double_set_point

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

    def get_errors(self) -> list[str]:
        """Return zone errors."""
        return self.errors

    def get_floor_demand(self) -> bool:
        """Return zone floor demand."""
        return self.floor_demand

    def get_id(self) -> int:
        """Return zone ID."""
        return self.id

    def get_heat_stage(self) -> AirzoneStages | None:
        """Return zone heat stage."""
        return self.heat_stage

    def get_heat_stages(self) -> list[AirzoneStages] | None:
        """Return zone heat stages."""
        if len(self.heat_stages) > 0:
            return self.heat_stages
        return None

    def get_humidity(self) -> int | None:
        """Return zone humidity."""
        if self.humidity is not None and self.humidity != 0:
            return self.humidity
        return None

    def get_master(self) -> bool:
        """Return zone master/slave."""
        return self.master

    def get_mode(self) -> OperationMode:
        """Return zone mode."""
        return self.mode

    def get_modes(self) -> list[OperationMode]:
        """Return zone modes."""
        if self.master:
            return self.modes
        modes = self.system.get_modes()
        if len(modes) == 0:
            modes = [self.mode]
            if OperationMode.STOP not in modes:
                modes.append(OperationMode.STOP)
        return modes

    def get_name(self) -> str:
        """Return zone name."""
        return self.name

    def get_on(self) -> bool:
        """Return zone on/off."""
        return self.on

    def get_problems(self) -> bool:
        """Return zone problems."""
        return bool(self.errors)

    def get_speed(self) -> int | None:
        """Return zone speed."""
        return self.speed

    def get_speeds(self) -> int | None:
        """Return zone speeds."""
        return self.speeds

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
