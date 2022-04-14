"""Airzone Local API Config."""

from aioairzone.common import ConnectionOptions
from aioairzone.const import DEFAULT_PORT, DEFAULT_SYSTEM_ID

AIRZONE_OPTIONS = ConnectionOptions("192.168.1.25", DEFAULT_PORT, DEFAULT_SYSTEM_ID)
