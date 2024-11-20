"""Airzone Local API Device."""

from __future__ import annotations

from typing import Any

from .common import (
    AirzoneStages,
    EcoAdapt,
    GrilleAngle,
    OperationAction,
    OperationMode,
    SleepTimeout,
    TemperatureUnit,
    get_system_zone_id,
)
from .const import (
    API_AIR_DEMAND,
    API_ANTI_FREEZE,
    API_BUG_MAX_TEMP_FAH,
    API_BUG_MIN_TEMP_FAH,
    API_COLD_ANGLE,
    API_COLD_DEMAND,
    API_COLD_STAGE,
    API_COLD_STAGES,
    API_COOL_MAX_TEMP,
    API_COOL_MIN_TEMP,
    API_COOL_SET_POINT,
    API_DOUBLE_SET_POINT,
    API_DOUBLE_SET_POINT_PARAMS,
    API_ECO_ADAPT,
    API_ERROR_LOW_BATTERY,
    API_ERRORS,
    API_FLOOR_DEMAND,
    API_HEAT_ANGLE,
    API_HEAT_DEMAND,
    API_HEAT_MAX_TEMP,
    API_HEAT_MIN_TEMP,
    API_HEAT_SET_POINT,
    API_HEAT_STAGE,
    API_HEAT_STAGES,
    API_HUMIDITY,
    API_MASTER_ZONE_ID,
    API_MAX_TEMP,
    API_MIN_TEMP,
    API_MODE,
    API_MODES,
    API_NAME,
    API_ON,
    API_ROOM_TEMP,
    API_SET_POINT,
    API_SLEEP,
    API_SPEED,
    API_SPEEDS,
    API_TEMP_STEP,
    API_UNITS,
    AZD_ABS_TEMP_MAX,
    AZD_ABS_TEMP_MIN,
    AZD_ACTION,
    AZD_AIR_DEMAND,
    AZD_ANTI_FREEZE,
    AZD_AVAILABLE,
    AZD_BATTERY_LOW,
    AZD_COLD_ANGLE,
    AZD_COLD_DEMAND,
    AZD_COLD_STAGE,
    AZD_COLD_STAGES,
    AZD_COOL_TEMP_MAX,
    AZD_COOL_TEMP_MIN,
    AZD_COOL_TEMP_SET,
    AZD_DEMAND,
    AZD_DOUBLE_SET_POINT,
    AZD_ECO_ADAPT,
    AZD_ERRORS,
    AZD_FLOOR_DEMAND,
    AZD_FULL_NAME,
    AZD_HEAT_ANGLE,
    AZD_HEAT_DEMAND,
    AZD_HEAT_STAGE,
    AZD_HEAT_STAGES,
    AZD_HEAT_TEMP_MAX,
    AZD_HEAT_TEMP_MIN,
    AZD_HEAT_TEMP_SET,
    AZD_HUMIDITY,
    AZD_ID,
    AZD_MASTER,
    AZD_MASTER_ZONE,
    AZD_MODE,
    AZD_MODES,
    AZD_NAME,
    AZD_ON,
    AZD_PROBLEMS,
    AZD_SLEEP,
    AZD_SPEED,
    AZD_SPEEDS,
    AZD_SYSTEM,
    AZD_TEMP,
    AZD_TEMP_MAX,
    AZD_TEMP_MIN,
    AZD_TEMP_SET,
    AZD_TEMP_STEP,
    AZD_TEMP_UNIT,
    AZD_THERMOSTAT_FW,
    AZD_THERMOSTAT_MODEL,
    AZD_THERMOSTAT_RADIO,
    DEFAULT_TEMP_MAX_CELSIUS,
    DEFAULT_TEMP_MAX_FAHRENHEIT,
    DEFAULT_TEMP_MIN_CELSIUS,
    DEFAULT_TEMP_MIN_FAHRENHEIT,
    DEFAULT_TEMP_STEP_CELSIUS,
    DEFAULT_TEMP_STEP_FAHRENHEIT,
    ERROR_ZONE,
)
from .thermostat import Thermostat


class Zone:
    """Airzone Zone."""

    def __init__(self, system_id: int, zone_id: int, zone_data: dict[str, Any]):
        """Zone init."""
        self.air_demand: bool | None = None
        self.anti_freeze: bool | None = None
        self.available: bool = True
        self.cold_angle: GrilleAngle | None = None
        self.cold_demand: bool | None = None
        self.cold_stage: AirzoneStages | None = None
        self.cold_stages: list[AirzoneStages] = []
        self.cool_temp_max: float | None = None
        self.cool_temp_min: float | None = None
        self.cool_temp_set: float | None = None
        self.double_set_point: bool | None = None
        self.eco_adapt: EcoAdapt | None = None
        self.errors: list[str] = []
        self.floor_demand: bool | None = None
        self.heat_angle: GrilleAngle | None = None
        self.heat_demand: bool | None = None
        self.heat_temp_max: float | None = None
        self.heat_temp_min: float | None = None
        self.heat_temp_set: float | None = None
        self.heat_stage: AirzoneStages | None = None
        self.heat_stages: list[AirzoneStages] = []
        self.humidity: int | None = None
        self.id = zone_id
        self.master_zone: int | None = None
        self.mode: OperationMode
        self.modes: list[OperationMode] = []
        self.on: bool
        self.sleep: SleepTimeout | None = None
        self.speed: int | None = None
        self.speeds: list[int] = []
        self.system_id: int = system_id
        self.system_zone_id: str = get_system_zone_id(system_id, zone_id)
        self.temp_set: float | None = None

        self.name: str = f"Airzone {self.get_system_zone_id()}"

        self.update_data(zone_data)

    def update_data(self, zone_data: dict[str, Any]) -> None:
        """Update Zone data."""
        self.available = True

        self.double_set_point_params: bool = (
            zone_data.keys() >= API_DOUBLE_SET_POINT_PARAMS
        )
        self.master = bool(API_MODES in zone_data)
        self.on = bool(zone_data[API_ON])
        self.temp = float(zone_data[API_ROOM_TEMP])
        self.temp_max = float(zone_data[API_MAX_TEMP])
        self.temp_min = float(zone_data[API_MIN_TEMP])
        self.temp_step: float | None = None
        self.temp_unit = TemperatureUnit(zone_data[API_UNITS])
        self.thermostat = Thermostat(zone_data)

        if API_MASTER_ZONE_ID in zone_data:
            master_zone_id = int(zone_data[API_MASTER_ZONE_ID])
            if master_zone_id != self.id:
                self.master_zone = master_zone_id

        if API_AIR_DEMAND in zone_data:
            self.air_demand = bool(zone_data[API_AIR_DEMAND])
        if API_FLOOR_DEMAND in zone_data:
            self.floor_demand = bool(zone_data[API_FLOOR_DEMAND])

        if API_ANTI_FREEZE in zone_data:
            self.anti_freeze = bool(zone_data[API_ANTI_FREEZE])

        if API_COLD_DEMAND in zone_data:
            self.cold_demand = bool(zone_data[API_COLD_DEMAND])
        if API_HEAT_DEMAND in zone_data:
            self.heat_demand = bool(zone_data[API_HEAT_DEMAND])

        if API_DOUBLE_SET_POINT in zone_data:
            self.double_set_point = bool(zone_data[API_DOUBLE_SET_POINT])

        if API_ECO_ADAPT in zone_data:
            self.eco_adapt = EcoAdapt(zone_data[API_ECO_ADAPT])

        if API_HUMIDITY in zone_data:
            self.humidity = int(zone_data[API_HUMIDITY])

        if API_COLD_ANGLE in zone_data:
            self.cold_angle = GrilleAngle(zone_data[API_COLD_ANGLE])
        if API_HEAT_ANGLE in zone_data:
            self.heat_angle = GrilleAngle(zone_data[API_HEAT_ANGLE])

        if API_COLD_STAGE in zone_data:
            self.cold_stage = AirzoneStages(zone_data[API_COLD_STAGE])
        if API_COLD_STAGES in zone_data:
            cold_stages = AirzoneStages(zone_data[API_COLD_STAGES])
            self.cold_stages = cold_stages.to_list()
        elif self.cold_stage and self.cold_stage.exists():
            self.cold_stages = [self.cold_stage]

        if API_HEAT_STAGE in zone_data:
            self.heat_stage = AirzoneStages(zone_data[API_HEAT_STAGE])
        if API_HEAT_STAGES in zone_data:
            heat_stages = AirzoneStages(zone_data[API_HEAT_STAGES])
            self.heat_stages = heat_stages.to_list()
        elif self.heat_stage and self.heat_stage.exists():
            self.heat_stages = [self.heat_stage]

        if API_COOL_MAX_TEMP in zone_data:
            self.cool_temp_max = float(zone_data[API_COOL_MAX_TEMP])
        if API_COOL_MIN_TEMP in zone_data:
            self.cool_temp_min = float(zone_data[API_COOL_MIN_TEMP])
        if API_COOL_SET_POINT in zone_data:
            cool_temp_set = self.validate_temp_set(
                float(zone_data[API_COOL_SET_POINT]), self.cool_temp_max
            )
            if cool_temp_set is not None:
                self.cool_temp_set = cool_temp_set

        if API_HEAT_MAX_TEMP in zone_data:
            self.heat_temp_max = float(zone_data[API_HEAT_MAX_TEMP])
        if API_HEAT_MIN_TEMP in zone_data:
            self.heat_temp_min = float(zone_data[API_HEAT_MIN_TEMP])
        if API_HEAT_SET_POINT in zone_data:
            heat_temp_set = self.validate_temp_set(
                float(zone_data[API_HEAT_SET_POINT]), self.heat_temp_max
            )
            if heat_temp_set is not None:
                self.heat_temp_set = heat_temp_set

        if API_ERRORS in zone_data:
            errors: list[dict[str, str]] = zone_data[API_ERRORS]
            for error in errors:
                for key, val in error.items():
                    self.add_error(key, val)

        if API_MODE in zone_data:
            self.mode = OperationMode(zone_data[API_MODE])
        else:
            self.master = True
            self.mode = OperationMode.AUTO
            self.modes = [self.mode]

        if self.master:
            if API_MODES in zone_data:
                self.modes = []
                for mode in zone_data[API_MODES]:
                    self.modes += [OperationMode(mode)]

        if API_NAME in zone_data:
            self.name = str(zone_data[API_NAME])

        if API_SLEEP in zone_data:
            self.sleep = SleepTimeout(zone_data[API_SLEEP])

        if API_SPEED in zone_data:
            self.speed = int(zone_data[API_SPEED])
        if API_SPEEDS in zone_data:
            speeds = int(zone_data[API_SPEEDS])
            self.speeds = list(range(0, speeds + 1))

        if API_SET_POINT in zone_data:
            temp_set = self.validate_temp_set(
                float(zone_data[API_SET_POINT]), self.temp_max
            )
            if temp_set is not None:
                self.temp_set = temp_set
        if API_TEMP_STEP in zone_data:
            self.temp_step = float(zone_data[API_TEMP_STEP])
        else:
            if self.temp_unit == TemperatureUnit.FAHRENHEIT:
                self.temp_step = DEFAULT_TEMP_STEP_FAHRENHEIT
            else:
                self.temp_step = DEFAULT_TEMP_STEP_CELSIUS

    def data(self) -> dict[str, Any]:
        """Return Airzone zone data."""
        data = {
            AZD_ABS_TEMP_MAX: self.get_abs_temp_max(),
            AZD_ABS_TEMP_MIN: self.get_abs_temp_min(),
            AZD_ACTION: self.get_action(),
            AZD_AVAILABLE: self.get_available(),
            AZD_DEMAND: self.get_demand(),
            AZD_DOUBLE_SET_POINT: self.get_double_set_point(),
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
            AZD_TEMP_UNIT: self.get_temp_unit(),
        }

        air_demand = self.get_air_demand()
        if air_demand is not None:
            data[AZD_AIR_DEMAND] = air_demand

        floor_demand = self.get_floor_demand()
        if floor_demand is not None:
            data[AZD_FLOOR_DEMAND] = floor_demand

        anti_freeze = self.get_anti_freeze()
        if anti_freeze is not None:
            data[AZD_ANTI_FREEZE] = anti_freeze

        eco_adapt = self.get_eco_adapt()
        if eco_adapt is not None:
            data[AZD_ECO_ADAPT] = eco_adapt

        full_name = self.get_full_name()
        if full_name is not None:
            data[AZD_FULL_NAME] = full_name

        humidity = self.get_humidity()
        if humidity is not None:
            data[AZD_HUMIDITY] = humidity

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

        cold_angle = self.get_cold_angle()
        if cold_angle is not None:
            data[AZD_COLD_ANGLE] = cold_angle
        heat_angle = self.get_heat_angle()
        if heat_angle is not None:
            data[AZD_HEAT_ANGLE] = heat_angle

        cold_demand = self.get_cold_demand()
        if cold_demand is not None:
            data[AZD_COLD_DEMAND] = cold_demand
        heat_demand = self.get_heat_demand()
        if heat_demand is not None:
            data[AZD_HEAT_DEMAND] = heat_demand

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

        sleep = self.get_sleep()
        if sleep is not None:
            data[AZD_SLEEP] = sleep

        speed = self.get_speed()
        if speed is not None:
            data[AZD_SPEED] = speed
        speeds = self.get_speeds()
        if speeds is not None:
            data[AZD_SPEEDS] = speeds

        errors = self.get_errors()
        if len(errors) > 0:
            data[AZD_ERRORS] = errors

        master_zone = self.get_master_zone()
        if master_zone is not None:
            data[AZD_MASTER_ZONE] = master_zone

        modes = self.get_modes()
        if modes is not None:
            data[AZD_MODES] = modes

        temp_set = self.get_temp_set()
        if temp_set is not None:
            data[AZD_TEMP_SET] = temp_set
        temp_step = self.get_temp_step()
        if temp_step is not None:
            data[AZD_TEMP_STEP] = temp_step

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
        """Add zone error."""
        _key = key.casefold()
        if _key == ERROR_ZONE and val not in self.errors:
            self.errors += [val]

    def fix_max_temp(self, max_temp: float) -> float:
        """Fix possibly bugged max temperatures."""
        temp_unit = self.get_temp_unit()
        if temp_unit == TemperatureUnit.FAHRENHEIT:
            if max_temp >= API_BUG_MAX_TEMP_FAH:
                max_temp = max_temp / 10
            elif max_temp <= API_BUG_MIN_TEMP_FAH:
                max_temp = max_temp * 10
        if max_temp == 0.0:
            if temp_unit == TemperatureUnit.FAHRENHEIT:
                max_temp = DEFAULT_TEMP_MAX_FAHRENHEIT
            else:
                max_temp = DEFAULT_TEMP_MAX_CELSIUS
        return round(max_temp, 1)

    def fix_min_temp(self, min_temp: float) -> float:
        """Fix possibly bugged min temperatures."""
        temp_unit = self.get_temp_unit()
        if temp_unit == TemperatureUnit.FAHRENHEIT:
            if min_temp <= API_BUG_MIN_TEMP_FAH:
                min_temp = min_temp * 10
        if min_temp == 0.0:
            if temp_unit == TemperatureUnit.FAHRENHEIT:
                min_temp = DEFAULT_TEMP_MIN_FAHRENHEIT
            else:
                min_temp = DEFAULT_TEMP_MIN_CELSIUS
        return round(min_temp, 1)

    def get_abs_temp_max(self) -> float:
        """Return absolute max temp."""
        temps = [
            self.get_cool_temp_max(),
            self.get_heat_temp_max(),
            self.get_temp_max(),
        ]
        return max(list(temp for temp in temps if temp is not None))

    def get_abs_temp_min(self) -> float:
        """Return absolute min temp."""
        temps = [
            self.get_cool_temp_min(),
            self.get_heat_temp_min(),
            self.get_temp_min(),
        ]
        return min(list(temp for temp in temps if temp is not None))

    def get_action(self) -> OperationAction:
        """Return zone action."""

        if self.get_on():
            if self.get_demand():
                mode = self.get_mode()
                if mode == OperationMode.COOLING:
                    action = OperationAction.COOLING
                elif mode in [OperationMode.AUX_HEATING, OperationMode.HEATING]:
                    action = OperationAction.HEATING
                elif mode == OperationMode.FAN:
                    action = OperationAction.FAN
                elif mode == OperationMode.DRY:
                    action = OperationAction.DRYING
                elif mode == OperationMode.AUTO:
                    action = self.get_auto_mode()
                else:
                    action = OperationAction.OFF
            else:
                action = OperationAction.IDLE
        else:
            action = OperationAction.OFF

        return action

    def get_air_demand(self) -> bool | None:
        """Return zone air demand."""
        if self.air_demand is not None and self.is_stage_supported(AirzoneStages.Air):
            return self.air_demand
        return None

    def get_anti_freeze(self) -> bool | None:
        """Return zone anti freeze."""
        return self.anti_freeze

    def get_auto_mode(self) -> OperationAction:
        """Return action from auto mode."""
        temp_sp = self.get_temp_set()
        temp_min = self.get_temp_min()
        temp_max = self.get_temp_max()
        cool_sp = self.get_cool_temp_set()
        cool_max = self.get_cool_temp_max()
        cool_min = self.get_cool_temp_min()
        heat_sp = self.get_heat_temp_set()
        heat_max = self.get_heat_temp_max()
        heat_min = self.get_heat_temp_min()

        if (
            cool_max is not None
            and cool_min is not None
            and heat_max is not None
            and heat_min is not None
        ):
            cool_match = cool_max == temp_max and cool_min == temp_min
            heat_match = heat_max == temp_max and heat_min == temp_min

            if cool_match and not heat_match:
                return OperationAction.COOLING
            if heat_match and not cool_match:
                return OperationAction.HEATING

        if cool_sp is not None and heat_sp is not None:
            cool_match = cool_sp == temp_sp
            heat_match = heat_sp == temp_sp

            if cool_match and not heat_match:
                return OperationAction.COOLING
            if heat_match and not cool_match:
                return OperationAction.HEATING

        return OperationAction.IDLE

    def get_available(self) -> bool:
        """Return availability."""
        return self.available

    def get_battery_low(self) -> bool | None:
        """Return battery status."""
        if self.thermostat.get_radio():
            return API_ERROR_LOW_BATTERY in self.errors
        return None

    def get_cold_angle(self) -> GrilleAngle | None:
        """Return zone cold angle."""
        return self.cold_angle

    def get_cold_demand(self) -> bool | None:
        """Return zone cold demand."""
        return self.cold_demand

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
        if self.cool_temp_max is not None:
            return self.fix_max_temp(self.cool_temp_max)
        return None

    def get_cool_temp_min(self) -> float | None:
        """Return zone minimum cool temperature."""
        if self.cool_temp_min is not None:
            return self.fix_min_temp(self.cool_temp_min)
        return None

    def get_cool_temp_set(self) -> float | None:
        """Return zone set cool temperature."""
        if self.cool_temp_set:
            return round(self.cool_temp_set, 1)
        return None

    def get_demand(self) -> bool:
        """Return zone demand."""
        return bool(self.air_demand) or bool(self.floor_demand)

    def get_double_set_point(self) -> bool:
        """Return zone double set point."""
        if self.double_set_point_params:
            if self.double_set_point is not None:
                return self.double_set_point
            return OperationMode.AUTO in self.get_modes()
        return False

    def get_eco_adapt(self) -> EcoAdapt | None:
        """Return zone echo adapt."""
        return self.eco_adapt

    def get_errors(self) -> list[str]:
        """Return zone errors."""
        return self.errors

    def get_floor_demand(self) -> bool | None:
        """Return zone floor demand."""
        if self.floor_demand is not None and self.is_stage_supported(
            AirzoneStages.Radiant
        ):
            return self.floor_demand
        return None

    def get_full_name(self) -> str:
        """Return full name."""
        return f"Airzone [{self.get_system_zone_id()}] {self.get_name()}"

    def get_id(self) -> int:
        """Return zone ID."""
        return self.id

    def get_heat_angle(self) -> GrilleAngle | None:
        """Return zone heat angle."""
        return self.heat_angle

    def get_heat_demand(self) -> bool | None:
        """Return zone heat demand."""
        return self.heat_demand

    def get_heat_stage(self) -> AirzoneStages | None:
        """Return zone heat stage."""
        return self.heat_stage

    def get_heat_stages(self) -> list[AirzoneStages] | None:
        """Return zone heat stages."""
        if len(self.heat_stages) > 0:
            return self.heat_stages
        return None

    def get_heat_temp_max(self) -> float | None:
        """Return zone maximum heat temperature."""
        if self.heat_temp_max is not None:
            return self.fix_max_temp(self.heat_temp_max)
        return None

    def get_heat_temp_min(self) -> float | None:
        """Return zone minimum heat temperature."""
        if self.heat_temp_min is not None:
            return self.fix_min_temp(self.heat_temp_min)
        return None

    def get_heat_temp_set(self) -> float | None:
        """Return zone set heat temperature."""
        if self.heat_temp_set:
            return round(self.heat_temp_set, 1)
        return None

    def get_humidity(self) -> int | None:
        """Return zone humidity."""
        if self.humidity is not None and self.humidity != 0:
            return self.humidity
        return None

    def get_master(self) -> bool:
        """Return zone master/slave."""
        return self.master

    def get_master_zone(self) -> int | None:
        """Return corresponding master zone."""
        return self.master_zone

    def get_mode(self) -> OperationMode:
        """Return zone mode."""
        return self.mode

    def get_modes(self) -> list[OperationMode]:
        """Return zone modes."""
        modes = self.modes

        if len(modes) == 0 and self.mode is not None:
            modes = [self.mode]

        if OperationMode.STOP not in modes:
            modes += [OperationMode.STOP]

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

    def get_sleep(self) -> SleepTimeout | None:
        """Return zone sleep time in minutes."""
        return self.sleep

    def get_speed(self) -> int | None:
        """Return zone speed."""
        return self.speed

    def get_speeds(self) -> list[int] | None:
        """Return zone speeds."""
        if len(self.speeds) > 0:
            return self.speeds
        return None

    def get_system_id(self) -> int | None:
        """Return system ID."""
        return self.system_id

    def get_system_zone_id(self) -> str:
        """Return combined system and zone ID."""
        return self.system_zone_id

    def get_temp(self) -> float:
        """Return zone temperature."""
        return round(self.temp, 2)

    def get_temp_max(self) -> float:
        """Return zone maximum temperature."""
        return self.fix_max_temp(self.temp_max)

    def get_temp_min(self) -> float:
        """Return zone minimum temperature."""
        return self.fix_min_temp(self.temp_min)

    def get_temp_set(self) -> float | None:
        """Return zone set temperature."""
        if self.temp_set is not None:
            return round(self.temp_set, 1)
        return None

    def get_temp_step(self) -> float | None:
        """Return zone step temperature."""
        if self.temp_step is not None:
            return round(self.temp_step, 1)
        return None

    def get_temp_unit(self) -> TemperatureUnit:
        """Return zone temperature unit."""
        return self.temp_unit

    def is_stage_supported(self, stage: AirzoneStages) -> bool:
        """Check if Airzone Stage is supported."""
        cold_stages = self.get_cold_stages()
        if cold_stages is not None:
            if stage in cold_stages:
                return True
            if len(cold_stages) == 0:
                return True

        heat_stages = self.get_heat_stages()
        if heat_stages is not None:
            if stage in heat_stages:
                return True
            if len(heat_stages) == 0:
                return True

        return cold_stages is None and heat_stages is None

    def set_available(self, available: bool) -> None:
        """Set availability."""
        self.available = available

    def set_modes(self, modes: list[OperationMode]) -> None:
        """Set zone modes."""
        self.modes = modes

    def set_param(self, key: str, value: Any) -> None:
        """Update zone parameter by key and value."""
        if key == API_ANTI_FREEZE:
            self.anti_freeze = bool(value)
        elif key == API_COOL_SET_POINT:
            self.cool_temp_set = float(value)
        elif key == API_COLD_ANGLE:
            self.cold_angle = GrilleAngle(value)
        elif key == API_COLD_STAGE:
            self.cold_stage = AirzoneStages(value)
        elif key == API_ECO_ADAPT:
            self.eco_adapt = EcoAdapt(value)
        elif key == API_HEAT_ANGLE:
            self.heat_angle = GrilleAngle(value)
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
        elif key == API_SLEEP:
            self.sleep = SleepTimeout(value)
        elif key == API_SPEED:
            self.speed = int(value)

    def validate_temp_set(self, temp_set: float, max_val: float | None) -> float | None:
        """Validate Zone temp set against its maximum value."""
        if max_val is not None and max_val != 0.0:
            if temp_set <= max_val:
                return temp_set
            return None
        return temp_set
