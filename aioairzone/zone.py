"""Airzone Local API Zone."""
from __future__ import annotations

from typing import Any

from .common import AirzoneStages, OperationMode, TemperatureUnit
from .const import (
    API_AIR_DEMAND,
    API_COLD_STAGE,
    API_COLD_STAGES,
    API_COOL_MAX_TEMP,
    API_COOL_MIN_TEMP,
    API_COOL_SET_POINT,
    API_DOUBLE_SET_POINT,
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
    API_ROOM_TEMP,
    API_SET_POINT,
    API_SPEED,
    API_SPEEDS,
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
    ERROR_SYSTEM,
    ERROR_ZONE,
)
from .system import System
from .thermostat import Thermostat


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
        self.double_set_point: bool = False
        self.errors: list[str] = []
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
        self.speed: int | None = None
        self.speeds: int | None = None
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
        if API_DOUBLE_SET_POINT in zone:
            self.double_set_point = bool(zone[API_DOUBLE_SET_POINT])
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
            AZD_COLD_STAGE: self.get_cold_stage(),
            AZD_DEMAND: self.get_demand(),
            AZD_DOUBLE_SET_POINT: self.get_double_set_point(),
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

        if data[AZD_DOUBLE_SET_POINT]:
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

        if self.speed:
            data[AZD_SPEED] = self.speed
        if self.speeds:
            data[AZD_SPEEDS] = self.speeds

        if len(self.errors) > 0:
            data[AZD_ERRORS] = self.get_errors()

        modes = self.get_modes()
        if modes:
            data[AZD_MODES] = modes

        if self.thermostat.firmware:
            data[AZD_THERMOSTAT_FW] = self.thermostat.get_firmware()
        if self.thermostat.type:
            data[AZD_THERMOSTAT_MODEL] = self.thermostat.get_model()
        if self.thermostat.radio:
            data[AZD_THERMOSTAT_RADIO] = self.thermostat.get_radio()

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
        if self.master:
            return self.modes
        return self.system.get_modes()

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
        """Return zone speedS."""
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
