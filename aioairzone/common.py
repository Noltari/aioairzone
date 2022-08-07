"""Airzone library common code."""
from __future__ import annotations

from enum import IntEnum
from typing import Any


class AirzoneStages(IntEnum):
    """Airzone stages."""

    UNKNOWN = -1

    Off = 0
    Air = 1
    Radiant = 2
    Combined = 3

    @classmethod
    def _missing_(cls, value: Any) -> AirzoneStages:
        return cls.UNKNOWN

    def exists(self) -> bool:
        """Return if Airzone Stage exits."""
        return self.value != self.Off

    def to_list(self) -> list[AirzoneStages]:
        """Convert AirzoneStages value to list."""
        if self.value == self.Combined:
            return [
                AirzoneStages.Off,
                AirzoneStages.Air,
                AirzoneStages.Radiant,
                AirzoneStages.Combined,
            ]
        if self.value in (self.Air, self.Radiant):
            return [AirzoneStages.Off, self]
        return []


class GrilleAngle(IntEnum):
    """Airzone grille angles."""

    DEG_90 = 0
    DEG_50 = 1
    DEG_45 = 2
    DEG_40 = 3

    @classmethod
    def _missing_(cls, value: Any) -> GrilleAngle:
        return cls.DEG_90


class OperationMode(IntEnum):
    """Airzone operation modes."""

    UNKNOWN = -1

    STOP = 1
    COOLING = 2
    HEATING = 3
    FAN = 4
    DRY = 5
    AUTO = 7

    @classmethod
    def _missing_(cls, value: Any) -> OperationMode:
        return cls.UNKNOWN


class SleepTimeout(IntEnum):
    """Airzone sleep timeouts."""

    SLEEP_OFF = 0
    SLEEP_30 = 30
    SLEEP_60 = 60
    SLEEP_90 = 90

    @classmethod
    def _missing_(cls, value: Any) -> SleepTimeout:
        return cls.SLEEP_OFF


class SystemType(IntEnum):
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
    def _missing_(cls, value: Any) -> SystemType:
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


class TemperatureUnit(IntEnum):
    """Airzone temperature units."""

    CELSIUS = 0
    FAHRENHEIT = 1


class ThermostatType(IntEnum):
    """Airzone Thermostat Types."""

    UNKNOWN = -1

    Blueface = 1
    BluefaceZero = 2
    Lite = 3
    Think = 4

    @classmethod
    def _missing_(cls, value: Any) -> ThermostatType:
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


class WebServerInterface(IntEnum):
    """Airzone WebServer Interface type."""

    UNKNOWN = -1

    ETHERNET = 1
    WIFI = 2

    @classmethod
    def _missing_(cls, value: Any) -> WebServerInterface:
        return cls.UNKNOWN


class WebServerType(IntEnum):
    """Airzone WebServer Types."""

    UNKNOWN = -1

    AIRZONE = 1
    AIDOO = 2

    @classmethod
    def _missing_(cls, value: Any) -> WebServerType:
        return cls.UNKNOWN

    def __str__(self) -> str:
        """Convert WebServerType value to string."""
        models: dict[int, str] = {
            self.UNKNOWN: "Unknown",
            self.AIRZONE: "Airzone WebServer",
            self.AIDOO: "Aidoo WebServer",
        }
        return models[self.value]
