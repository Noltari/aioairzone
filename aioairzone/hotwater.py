"""Airzone Local API Domestic Hot Water."""

from __future__ import annotations

from typing import Any

from .common import (
    EntityType,
    HotWaterOperation,
    TemperatureUnit,
    parse_bool,
    parse_int,
)
from .const import (
    API_ACS_MAX_TEMP,
    API_ACS_MIN_TEMP,
    API_ACS_ON,
    API_ACS_POWER_MODE,
    API_ACS_SET_POINT,
    API_ACS_TEMP,
    API_UNITS,
    AZD_CONNECTED,
    AZD_NAME,
    AZD_ON,
    AZD_OPERATION,
    AZD_OPERATIONS,
    AZD_POWER_MODE,
    AZD_TEMP,
    AZD_TEMP_MAX,
    AZD_TEMP_MIN,
    AZD_TEMP_SET,
    AZD_TEMP_UNIT,
    MQTT_API_IS_CONNECTED,
    MQTT_API_MAX,
    MQTT_API_MIN,
    MQTT_API_PARAMETERS,
    MQTT_API_POWER,
    MQTT_API_POWERFUL_MODE,
    MQTT_API_RANGE_SP,
    MQTT_API_SETPOINT,
)
from .entity import Entity


class HotWater(Entity):
    """Airzone Domestic Hot Water."""

    def __init__(self, data: dict[str, Any]):
        """Hot Water init."""
        super().__init__(EntityType.HotWater)

        self.connected: bool | None = None
        self.name: str = "Airzone DHW"
        self.on: bool
        self.temp: int
        self.temp_max: int
        self.temp_min: int
        self.temp_set: int
        self.temp_unit: TemperatureUnit = TemperatureUnit.CELSIUS
        self.power_mode: bool | None = None

        self.update_data(data)

    def update_data(self, data: dict[str, Any]) -> None:
        """Update Hot Water data."""
        self.on = bool(data[API_ACS_ON])
        self.temp = int(data[API_ACS_TEMP])
        self.temp_max = int(data[API_ACS_MAX_TEMP])
        self.temp_min = int(data[API_ACS_MIN_TEMP])
        self.temp_set = int(data[API_ACS_SET_POINT])

        acs_power_mode = parse_bool(data.get(API_ACS_POWER_MODE))
        if acs_power_mode is not None:
            self.power_mode = acs_power_mode

        units = parse_int(data.get(API_UNITS))
        if units is not None:
            self.temp_unit = TemperatureUnit(units)

    def update_mqtt(self, data: dict[str, Any]) -> None:
        """Perform Entity MQTT update."""
        params = data.get(MQTT_API_PARAMETERS)
        if params is None:
            return

        is_connected = parse_bool(params.get(MQTT_API_IS_CONNECTED))
        if is_connected is not None:
            self.connected = is_connected

        power = parse_bool(params.get(MQTT_API_POWER))
        if power is not None:
            self.on = power

        powerful_mode = parse_bool(params.get(MQTT_API_POWERFUL_MODE))
        if powerful_mode is not None:
            self.power_mode = powerful_mode

        range_sp: dict[str, Any] | None = params.get(MQTT_API_RANGE_SP)
        if range_sp is not None:
            range_sp_max = parse_int(range_sp.get(MQTT_API_MAX))
            if range_sp_max is not None:
                self.temp_max = range_sp_max

            range_sp_min = parse_int(range_sp.get(MQTT_API_MIN))
            if range_sp_min is not None:
                self.temp_min = range_sp_min

        setpoint = parse_int(params.get(MQTT_API_SETPOINT))
        if setpoint is not None:
            self.temp_set = setpoint

    def data(self) -> dict[str, Any]:
        """Return Airzone Hot Water data."""
        data: dict[str, Any] = {
            AZD_CONNECTED: self.get_connected(),
            AZD_NAME: self.get_name(),
            AZD_ON: self.get_on(),
            AZD_OPERATION: self.get_operation(),
            AZD_OPERATIONS: self.get_operations(),
            AZD_TEMP: self.get_temp(),
            AZD_TEMP_MAX: self.get_temp_max(),
            AZD_TEMP_MIN: self.get_temp_min(),
            AZD_TEMP_SET: self.get_temp_set(),
            AZD_TEMP_UNIT: self.get_temp_unit(),
        }

        power_mode = self.get_power_mode()
        if power_mode is not None:
            data[AZD_POWER_MODE] = power_mode

        return data

    def get_connected(self) -> bool | None:
        """Return connection status."""
        return self.connected

    def get_name(self) -> str | None:
        """Return Hot Water name."""
        return self.name

    def get_on(self) -> bool:
        """Return Hot Water on/off."""
        return self.on

    def get_operation(self) -> HotWaterOperation:
        """Return Hot Water current operation."""
        if self.get_on():
            if self.get_power_mode():
                return HotWaterOperation.Powerful
            return HotWaterOperation.On
        return HotWaterOperation.Off

    def get_operations(self) -> list[HotWaterOperation]:
        """Return Hot Water operation list."""
        operations = [
            HotWaterOperation.Off,
            HotWaterOperation.On,
        ]
        if self.get_power_mode() is not None:
            operations += [HotWaterOperation.Powerful]
        return operations

    def get_power_mode(self) -> bool | None:
        """Return Hot Water power mode on/off."""
        if self.power_mode is not None:
            return self.power_mode
        return None

    def get_temp(self) -> int:
        """Return Hot Water temperature."""
        return self.temp

    def get_temp_max(self) -> int:
        """Return Hot Water max temperature."""
        return self.temp_max

    def get_temp_min(self) -> int:
        """Return Hot Water min temperature."""
        return self.temp_min

    def get_temp_set(self) -> int:
        """Return Hot Water set temperature."""
        return self.temp_set

    def get_temp_unit(self) -> TemperatureUnit:
        """Return Hot Water temperature unit."""
        return self.temp_unit

    def set_param(self, key: str, value: Any) -> None:
        """Update Hot Water parameter by key and value."""
        if key == API_ACS_ON:
            self.on = bool(value)
        elif key == API_ACS_POWER_MODE:
            if self.power_mode is not None:
                self.power_mode = bool(value)
        elif key == API_ACS_SET_POINT:
            self.temp_set = int(value)
