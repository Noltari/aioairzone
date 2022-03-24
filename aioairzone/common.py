"""Airzone library common code."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AirzoneStages(int, Enum):
    """Airzone stages."""

    Air = 1
    Radiant = 2
    Combined = 3

    def to_list(self) -> list[AirzoneStages]:
        """Convert AirzoneStages value to list."""
        if self.value == self.Combined:
            return [AirzoneStages.Air, AirzoneStages.Radiant, AirzoneStages.Combined]
        if self.value in (self.Air, self.Radiant):
            return [self]
        return []


@dataclass
class ConnectionOptions:
    """Airzone options for connection."""

    ip_address: str
    port: int


class OperationMode(int, Enum):
    """Airzone operation modes."""

    STOP = 1
    COOLING = 2
    HEATING = 3
    FAN = 4
    DRY = 5
    AUTO = 7


class TemperatureUnit(int, Enum):
    """Airzone temperature units."""

    CELSIUS = 0
    FAHRENHEIT = 1


class ThermostatType(int, Enum):
    """Airzone Thermostat Types."""

    Blueface = 1
    BluefaceZero = 2
    Lite = 3
    Think = 4

    def __str__(self) -> str:
        """Convert ThermostatType value to string."""
        models: dict[int, str] = {
            self.Blueface: "Blueface",
            self.BluefaceZero: "Blueface Zero",
            self.Lite: "Lite",
            self.Think: "Think",
        }
        return models[self.value]
