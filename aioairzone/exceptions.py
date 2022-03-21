"""Airzone library exceptions."""
from __future__ import annotations


class AirzoneError(Exception):
    """Base class for aioairzone errors."""


class APIError(AirzoneError):
    """Exception raised when API fails."""


class InvalidHost(AirzoneError):
    """Exception raised when invalid host is requested."""


class InvalidParam(AirzoneError):
    """Exception raised when invalid param is requested."""


class InvalidSystem(AirzoneError):
    """Exception raised when invalid system is requested."""


class InvalidZone(AirzoneError):
    """Exception raised when invalid zone is requested."""


class ParamUpdateFailure(AirzoneError):
    """Exception raised when parameter isn't updated."""
