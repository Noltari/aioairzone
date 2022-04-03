"""Airzone Local API Thermostat."""
from __future__ import annotations

from typing import Any

from .common import ThermostatType
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
