"""Airzone exceptions."""
from __future__ import annotations


class AirzoneError(Exception):
    """Base class for aioairzone errors."""


class InvalidHost(AirzoneError):
    """Exception raised when invalid system is requested."""


class InvalidSystem(AirzoneError):
    """Exception raised when invalid system is requested."""


class InvalidZone(AirzoneError):
    """Exception raised when invalid zone is requested."""
