"""Airzone Local API System."""
from __future__ import annotations

import logging
from typing import Any

from .common import OperationMode, SystemType
from .const import (
    API_POWER,
    API_SYSTEM_FIRMWARE,
    API_SYSTEM_ID,
    API_SYSTEM_TYPE,
    AZD_ERRORS,
    AZD_FIRMWARE,
    AZD_ID,
    AZD_MODEL,
    AZD_POWER,
    AZD_PROBLEMS,
    AZD_ZONES_NUM,
)
from .exceptions import InvalidZone
from .zone import Zone

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

        if len(self.errors) > 0:
            data[AZD_ERRORS] = self.get_errors()

        if self.firmware:
            data[AZD_FIRMWARE] = self.get_firmware()

        if self.type:
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
