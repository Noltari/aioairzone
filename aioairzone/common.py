"""Airzone library common code."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AirzoneStages(int, Enum):
    """Airzone stages."""

    UNKNOWN = -1

    Air = 1
    Radiant = 2
    Combined = 3

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN

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

    UNKNOWN = -1

    STOP = 1
    COOLING = 2
    HEATING = 3
    FAN = 4
    DRY = 5
    AUTO = 7

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN


class SystemType(int, Enum):
    """Airzone System Types."""

    UNKNOWN = -1

    C6 = 1
    AQUAGLASS = 2
    DZK = 3
    RADIANT = 4
    C3 = 5
    ZBS = 6
    ZS6 = 7

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN

    def __str__(self) -> str:
        """Convert ThermostatType value to string."""
        models: dict[int, str] = {
            self.UNKNOWN: "Unknown",
            self.C6: "C6",
            self.AQUAGLASS: "AQUAGLASS",
            self.DZK: "DZK",
            self.RADIANT: "Radiant",
            self.C3: "C3",
            self.ZBS: "ZBS",
            self.ZS6: "ZS6",
        }
        return models[self.value]


class TemperatureUnit(int, Enum):
    """Airzone temperature units."""

    CELSIUS = 0
    FAHRENHEIT = 1


class ThermostatType(int, Enum):
    """Airzone Thermostat Types."""

    UNKNOWN = -1

    Blueface = 1
    BluefaceZero = 2
    Lite = 3
    Think = 4

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN

    def __str__(self) -> str:
        """Convert ThermostatType value to string."""
        models: dict[int, str] = {
            self.UNKNOWN: "Unknown",
            self.Blueface: "Blueface",
            self.BluefaceZero: "Blueface Zero",
            self.Lite: "Lite",
            self.Think: "Think",
        }
        return models[self.value]

    def exists_radio(self) -> bool:
        """Return if a radio version of the Thermostat exists."""
        models: dict[int, bool] = {
            self.UNKNOWN: False,
            self.Blueface: False,
            self.BluefaceZero: False,
            self.Lite: True,
            self.Think: True,
        }
        return models[self.value]


class WebServerInterface(int, Enum):
    """Airzone WebServer Interface type."""

    UNKNOWN = -1

    ETHERNET = 1
    WIFI = 2

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN
