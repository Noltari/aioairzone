"""Airzone Local API WebServer."""

import random
from typing import Any

from aiohttp.web_response import Response
from helpers import api_json_response

from aioairzone.const import (
    API_INTERFACE,
    API_MAC,
    API_WIFI,
    API_WIFI_CHANNEL,
    API_WIFI_QUALITY,
    API_WIFI_RSSI,
    API_WS_AZ,
    API_WS_FIRMWARE,
    API_WS_TYPE,
)


class AirzoneWebServer:
    """Airzone Local API WebServer."""

    def __init__(self, mac: str) -> None:
        """Local API WebServer init."""
        self.firmware: str = "3.44"
        self.interface: str = API_WIFI
        self.mac: str = mac
        self.type: str = API_WS_AZ
        self.wifi_channel: int = 6
        self.wifi_rssi: int = -50

    def wifi_quality(self) -> int:
        """Convert Wifi RSSI to Quality."""
        quality: float
        if self.wifi_rssi <= -100:
            quality = 0
        elif self.wifi_rssi >= -50:
            quality = 100
        else:
            quality = 2 * (self.wifi_rssi + 100)
            quality = round(quality / 10, 0) * 10
        return int(quality)

    def data(self) -> dict[str, Any]:
        """Return Local API Version data."""
        return {
            API_INTERFACE: API_WIFI,
            API_MAC: self.mac,
            API_WIFI_CHANNEL: self.wifi_channel,
            API_WIFI_QUALITY: self.wifi_quality(),
            API_WIFI_RSSI: self.wifi_rssi,
            API_WS_FIRMWARE: self.firmware,
            API_WS_TYPE: self.type,
        }

    def refresh(self) -> None:
        """Refresh Local API WebServer."""
        wifi_rssi = self.wifi_rssi + random.randrange(-10, 10, 1)
        if wifi_rssi <= -100:
            self.wifi_rssi = -100
        elif wifi_rssi >= -50:
            self.wifi_rssi = -50
        else:
            self.wifi_rssi = wifi_rssi

    async def post(self) -> Response:
        """POST Local API WebServer."""
        self.refresh()
        return api_json_response(self.data())
