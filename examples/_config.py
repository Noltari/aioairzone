"""Airzone Local API Config."""

from aioairzone.const import DEFAULT_PORT_HTTP, DEFAULT_SYSTEM_ID
from aioairzone.localapi import ConnectionOptions

AIRZONE_OPTIONS = ConnectionOptions(
    f"http://192.168.1.25:{DEFAULT_PORT_HTTP}",
    DEFAULT_SYSTEM_ID,
    True,
)
