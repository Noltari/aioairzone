"""Airzone Local API WebServer."""
from __future__ import annotations

from typing import Any

from .common import WebServerInterface
from .const import (
    API_INTERFACE,
    API_MAC,
    API_WIFI,
    API_WIFI_CHANNEL,
    API_WIFI_QUALITY,
    API_WIFI_SIGNAL,
    AZD_INTERFACE,
    AZD_MAC,
    AZD_WIFI_CHANNEL,
    AZD_WIFI_QUALITY,
    AZD_WIFI_SIGNAL,
)


class WebServer:
    """Airzone WebServer."""

    def __init__(self, data: dict[str, Any]):
        """WebServer init."""
        self.interface: WebServerInterface | None = None
        self.mac: str | None = None
        self.wifi_channel: int | None = None
        self.wifi_quality: int | None = None
        self.wifi_signal: int | None = None

        if API_INTERFACE in data:
            if data[API_INTERFACE] == API_WIFI:
                self.interface = WebServerInterface.WIFI
            else:
                self.interface = WebServerInterface.ETHERNET

        if API_MAC in data:
            self.mac = str(data[API_MAC])

        if API_WIFI_CHANNEL in data:
            self.wifi_channel = int(data[API_WIFI_CHANNEL])
        if API_WIFI_QUALITY in data:
            self.wifi_quality = int(data[API_WIFI_QUALITY])
        if API_WIFI_SIGNAL in data:
            self.wifi_signal = int(data[API_WIFI_SIGNAL])

    def data(self) -> dict[str, Any]:
        """Return Airzone system data."""
        data: dict[str, Any] = {}

        if self.interface is not None:
            data[AZD_INTERFACE] = self.get_interface()

        if self.mac is not None:
            data[AZD_MAC] = self.get_mac()

        if self.wifi_channel is not None:
            data[AZD_WIFI_CHANNEL] = self.get_wifi_channel()
        if self.wifi_quality is not None:
            data[AZD_WIFI_QUALITY] = self.get_wifi_quality()
        if self.wifi_signal is not None:
            data[AZD_WIFI_SIGNAL] = self.get_wifi_signal()

        return data

    def get_interface(self) -> WebServerInterface | None:
        """Return WebServer network interface."""
        return self.interface

    def get_mac(self) -> str | None:
        """Return WebServer MAC address."""
        return self.mac

    def get_wifi_channel(self) -> int | None:
        """Return WebServer wifi channel."""
        return self.wifi_channel

    def get_wifi_quality(self) -> int | None:
        """Return WebServer wifi quality."""
        return self.wifi_quality

    def get_wifi_signal(self) -> int | None:
        """Return WebServer wifi signal."""
        return self.wifi_signal
