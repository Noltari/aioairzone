"""Airzone Local API WebServer."""

from __future__ import annotations

from typing import Any

from .common import WebServerInterface, WebServerType, get_dict_cast
from .const import (
    API_INTERFACE,
    API_MAC,
    API_WIFI,
    API_WIFI_CHANNEL,
    API_WIFI_QUALITY,
    API_WIFI_RSSI,
    API_WS_AIDOO,
    API_WS_AZ,
    API_WS_FIRMWARE,
    API_WS_TYPE,
    AZD_FIRMWARE,
    AZD_FULL_NAME,
    AZD_INTERFACE,
    AZD_MAC,
    AZD_MODEL,
    AZD_WIFI_CHANNEL,
    AZD_WIFI_QUALITY,
    AZD_WIFI_RSSI,
)


class WebServer:
    """Airzone WebServer."""

    def __init__(self, data: dict[str, Any]):
        """WebServer init."""
        self.firmware: str | None = None
        self.interface: WebServerInterface | None = None
        self.mac: str | None = None
        self.type: WebServerType | None = None
        self.wifi_channel: int | None = None
        self.wifi_quality: int | None = None
        self.wifi_rssi: int | None = None
        self.update_data(data)

    def update_data(self, data: dict[str, Any]) -> None:
        """Update WebServer data."""
        interface = get_dict_cast(data, API_INTERFACE, str)
        if interface is not None:
            if interface == API_WIFI:
                self.interface = WebServerInterface.WIFI
            else:
                self.interface = WebServerInterface.ETHERNET

        mac = get_dict_cast(data, API_MAC, str)
        if mac is not None:
            self.mac = mac

        wifi_channel = get_dict_cast(data, API_WIFI_CHANNEL, int)
        if wifi_channel is not None:
            self.wifi_channel = int(data[API_WIFI_CHANNEL])
        wifi_quality = get_dict_cast(data, API_WIFI_QUALITY, int)
        if wifi_quality is not None:
            self.wifi_quality = int(data[API_WIFI_QUALITY])
        wifi_rssi = get_dict_cast(data, API_WIFI_RSSI, int)
        if wifi_rssi is not None:
            self.wifi_rssi = int(data[API_WIFI_RSSI])

        ws_firmware = get_dict_cast(data, API_WS_FIRMWARE, str)
        if ws_firmware is not None:
            self.firmware = ws_firmware

        ws_type = get_dict_cast(data, API_WS_TYPE, str)
        if ws_type is not None:
            if ws_type == API_WS_AZ:
                self.type = WebServerType.AIRZONE
            elif ws_type == API_WS_AIDOO:
                self.type = WebServerType.AIDOO
            else:
                self.type = WebServerType.UNKNOWN

    def data(self) -> dict[str, Any]:
        """Return Airzone system data."""
        data: dict[str, Any] = {}

        firmware = self.get_firmware()
        if firmware is not None:
            data[AZD_FIRMWARE] = firmware

        full_name = self.get_full_name()
        if full_name is not None:
            data[AZD_FULL_NAME] = full_name

        interface = self.get_interface()
        if interface is not None:
            data[AZD_INTERFACE] = interface

        mac = self.get_mac()
        if mac is not None:
            data[AZD_MAC] = mac

        model = self.get_model()
        if model is not None:
            data[AZD_MODEL] = model

        wifi_channel = self.get_wifi_channel()
        if wifi_channel is not None:
            data[AZD_WIFI_CHANNEL] = wifi_channel
        wifi_quality = self.get_wifi_quality()
        if wifi_quality is not None:
            data[AZD_WIFI_QUALITY] = wifi_quality
        wifi_rssi = self.get_wifi_rssi()
        if wifi_rssi is not None:
            data[AZD_WIFI_RSSI] = wifi_rssi

        return data

    def get_firmware(self) -> str | None:
        """Return WebServer firmware."""
        if self.firmware and "." not in self.firmware and len(self.firmware) > 2:
            return f"{self.firmware[0:1]}.{self.firmware[1:]}"
        return self.firmware

    def get_full_name(self) -> str | None:
        """Return full name."""
        return self.get_model()

    def get_interface(self) -> WebServerInterface | None:
        """Return WebServer network interface."""
        return self.interface

    def get_mac(self) -> str | None:
        """Return WebServer MAC address."""
        return self.mac

    def get_model(self) -> str | None:
        """Return WebServer model."""
        if self.type:
            return str(self.type)
        return None

    def get_wifi_channel(self) -> int | None:
        """Return WebServer wifi channel."""
        return self.wifi_channel

    def get_wifi_quality(self) -> int | None:
        """Return WebServer wifi quality."""
        return self.wifi_quality

    def get_wifi_rssi(self) -> int | None:
        """Return WebServer wifi RSSI."""
        return self.wifi_rssi
