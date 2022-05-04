"""Airzone library exceptions."""
from __future__ import annotations


class AirzoneError(Exception):
    """Base class for aioairzone errors."""


class APIError(AirzoneError):
    """Exception raised when API fails."""


class InvalidHost(AirzoneError):
    """Exception raised when invalid host is requested."""


class InvalidMethod(AirzoneError):
    """Exception raised when invalid method is requested."""


class InvalidParam(AirzoneError):
    """Exception raised when invalid param is requested."""


class InvalidSystem(AirzoneError):
    """Exception raised when invalid system is requested."""


class InvalidZone(AirzoneError):
    """Exception raised when invalid zone is requested."""


class ParamUpdateFailure(AirzoneError):
    """Exception raised when parameter isn't updated."""


class RequestMalformed(AirzoneError):
    """Exception raised when API receives a malformed request."""


class SystemOutOfRange(InvalidSystem):
    """Exception raised when system id is out of range."""


class SystemNotAvailable(InvalidSystem):
    """Exception raised when system id is not available."""


class ZoneOutOfRange(InvalidZone):
    """Exception raised when zone id is out of range."""


class ZoneNotAvailable(InvalidZone):
    """Exception raised when zone id is not available."""


class ZoneNotProvided(AirzoneError):
    """Exception raised when zone id is not provided."""
