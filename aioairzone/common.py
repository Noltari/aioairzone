"""Airzone library common code."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


def system_zone_id(system_id: int, zone_id: int) -> str:
    """Combine System and Zone IDs into a single ID."""
    return f"{system_id}:{zone_id}"


class AirzoneStages(int, Enum):
    """Airzone stages."""

    Air = 1
    Radiant = 2
    Combined = 3


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
