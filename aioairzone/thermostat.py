"""Airzone Local API Thermostat."""

from __future__ import annotations

from typing import Any, Final

from .common import ThermostatType, parse_bool, parse_int, parse_str
from .const import (
    API_BATTERY,
    API_COVERAGE,
    API_THERMOS_FIRMWARE,
    API_THERMOS_RADIO,
    API_THERMOS_TYPE,
    THERMOSTAT_RADIO,
    THERMOSTAT_WIRED,
)

LOW_BATTERY_VALUE: Final[int] = 35


class Thermostat:
    """Airzone Thermostat."""

    def __init__(self, data: dict[str, Any]):
        """Thermostat init."""
        self.battery: int | None = None
        self.firmware: str | None = None
        self.radio: bool | None = None
        self.signal: int | None = None
        self.type: ThermostatType | None = None

        thermos_battery = parse_int(data.get(API_BATTERY))
        if thermos_battery is not None:
            self.battery = thermos_battery

        thermos_firmware = parse_str(data.get(API_THERMOS_FIRMWARE))
        if thermos_firmware is not None:
            self.firmware = thermos_firmware

        thermos_radio = parse_bool(data.get(API_THERMOS_RADIO))
        if thermos_radio is not None:
            self.radio = thermos_radio

        thermos_signal = parse_int(data.get(API_COVERAGE))
        if thermos_signal is not None:
            self.signal = thermos_signal

        thermos_type = parse_int(data.get(API_THERMOS_TYPE))
        if thermos_type is not None:
            self.type = ThermostatType(thermos_type)

    def get_battery(self) -> int | None:
        """Return Airzone Thermostat battery."""
        return self.battery

    def get_battery_low(self) -> bool | None:
        """Return Airzone Thermostat low battery."""
        if not self.get_radio():
            return None
        if self.battery is None:
            return None
        return self.battery < LOW_BATTERY_VALUE

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

    def get_signal(self) -> int | None:
        """Return Airzone Thermostat signal."""
        return self.signal
