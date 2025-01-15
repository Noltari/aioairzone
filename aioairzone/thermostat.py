"""Airzone Local API Thermostat."""

from __future__ import annotations

from typing import Any

from .common import ThermostatType, parse_bool, parse_int, parse_str
from .const import (
    API_THERMOS_FIRMWARE,
    API_THERMOS_RADIO,
    API_THERMOS_TYPE,
    THERMOSTAT_RADIO,
    THERMOSTAT_WIRED,
)


class Thermostat:
    """Airzone Thermostat."""

    def __init__(self, data: dict[str, Any]):
        """Thermostat init."""
        self.firmware: str | None = None
        self.radio: bool | None = None
        self.type: ThermostatType | None = None

        thermos_firmware = parse_str(data.get(API_THERMOS_FIRMWARE))
        if thermos_firmware is not None:
            self.firmware = thermos_firmware
        thermos_radio = parse_bool(data.get(API_THERMOS_RADIO))
        if thermos_radio is not None:
            self.radio = thermos_radio
        thermos_type = parse_int(data.get(API_THERMOS_TYPE))
        if thermos_type is not None:
            self.type = ThermostatType(thermos_type)

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
