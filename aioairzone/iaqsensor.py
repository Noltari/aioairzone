"""Airzone Local API IAQ Sensor."""

from __future__ import annotations

from typing import Any

from .common import get_system_zone_id, parse_float, parse_int, parse_str
from .const import (
    API_CO2_VALUE,
    API_IAQ_INDEX,
    API_IAQ_SCORE,
    API_NAME,
    API_PM2_5_VALUE,
    API_PM10_VALUE,
    API_PRESSURE_VALUE,
    API_TVOC_VALUE,
    AZD_CO2,
    AZD_IAQ_INDEX,
    AZD_IAQ_SCORE,
    AZD_ID,
    AZD_NAME,
    AZD_PM2_5,
    AZD_PM10,
    AZD_PRESSURE,
    AZD_SYSTEM,
    AZD_TVOC,
)


class IAQSensor:
    """Airzone IAQ Sensor."""

    def __init__(self, system_id: int, sensor_id: int, data: dict[str, Any]):
        """IAQ Sensor init."""
        self.system_id = system_id
        self.sensor_id = sensor_id
        self.name: str = f"Airzone IAQ {system_id}:{sensor_id}"
        self.co2: float | None = None
        self.iaq_index: int | None = None
        self.iaq_score: int | None = None
        self.pm2_5: float | None = None
        self.pm10: float | None = None
        self.pressure: float | None = None
        self.tvoc: float | None = None
        self.update_data(data)

    def update_data(self, data: dict[str, Any]) -> None:
        """Update IAQ Sensor data."""
        name = parse_str(data.get(API_NAME))
        if name:
            self.name = name

        co2 = parse_float(data.get(API_CO2_VALUE))
        if co2 is not None:
            self.co2 = co2
        iaq_index = parse_int(data.get(API_IAQ_INDEX))
        if iaq_index is not None:
            self.iaq_index = iaq_index
        iaq_score = parse_int(data.get(API_IAQ_SCORE))
        if iaq_score is not None:
            self.iaq_score = iaq_score
        pm2_5 = parse_float(data.get(API_PM2_5_VALUE))
        if pm2_5 is not None:
            self.pm2_5 = pm2_5
        pm10 = parse_float(data.get(API_PM10_VALUE))
        if pm10 is not None:
            self.pm10 = pm10
        pressure = parse_float(data.get(API_PRESSURE_VALUE))
        if pressure is not None:
            self.pressure = pressure
        tvoc = parse_float(data.get(API_TVOC_VALUE))
        if tvoc is not None:
            self.tvoc = tvoc

    def data(self) -> dict[str, Any]:
        """Return Airzone IAQ Sensor data."""
        data: dict[str, Any] = {
            AZD_ID: self.sensor_id,
            AZD_NAME: self.get_name(),
            AZD_SYSTEM: self.system_id,
        }

        if self.co2 is not None:
            data[AZD_CO2] = self.co2
        if self.iaq_index is not None:
            data[AZD_IAQ_INDEX] = self.iaq_index
        if self.iaq_score is not None:
            data[AZD_IAQ_SCORE] = self.iaq_score
        if self.pm2_5 is not None:
            data[AZD_PM2_5] = self.pm2_5
        if self.pm10 is not None:
            data[AZD_PM10] = self.pm10
        if self.pressure is not None:
            data[AZD_PRESSURE] = self.pressure
        if self.tvoc is not None:
            data[AZD_TVOC] = self.tvoc

        return data

    def get_id(self) -> int:
        """Return IAQ Sensor ID."""
        return self.sensor_id

    def get_name(self) -> str:
        """Return IAQ Sensor name."""
        return self.name

    def get_system_id(self) -> int:
        """Return IAQ Sensor system ID."""
        return self.system_id

    def get_system_sensor_id(self) -> str:
        """Return IAQ Sensor system and sensor IDs."""
        return get_system_zone_id(self.system_id, self.sensor_id)
