"""Airzone Local API IAQ Sensor."""

import random
from typing import Any

from aiohttp import web
from aiohttp.web_response import Response
from helpers import api_json_error, api_json_response

from aioairzone.const import (
    API_CO2_VALUE,
    API_DATA,
    API_ERROR_IAQ_SENSOR_ID_NOT_AVAILABLE,
    API_ERROR_SYSTEM_ID_NOT_PROVIDED,
    API_IAQ_INDEX,
    API_IAQ_SCORE,
    API_IAQ_SENSOR_ID,
    API_NAME,
    API_PM2_5_VALUE,
    API_PM10_VALUE,
    API_PRESSURE_VALUE,
    API_SYSTEM_ID,
    API_SYSTEMS,
    API_TVOC_VALUE,
)


class AirzoneIAQSensor:
    """Airzone Local API IAQ Sensor."""

    def __init__(self, system: int, sensor: int) -> None:
        """Local API IAQ Sensor init."""
        self.system: int = system
        self.sensor: int = sensor
        self.name: str = ""
        self.co2: int = 585
        self.pm2_5: int = 4
        self.pm10: int = 5
        self.pressure: int = 1043
        self.score: int = 82
        self.tvoc: int = 95

    def refresh(self) -> None:
        """Refresh IAQ Sensor values."""
        self.co2 = min(max(self.co2 + random.randrange(-10, 11), 400), 2000)
        self.score = min(max(self.score + random.randrange(-2, 3), 0), 100)
        self.tvoc = min(max(self.tvoc + random.randrange(-5, 6), 0), 500)

    def index(self) -> int:
        """Return IAQ index from score."""
        if self.score >= 80:
            return 1
        if self.score >= 50:
            return 2
        return 3

    def data(self) -> dict[str, Any]:
        """Return Local API IAQ Sensor data."""
        return {
            API_SYSTEM_ID: self.system,
            API_IAQ_SENSOR_ID: self.sensor,
            API_NAME: self.name,
            API_IAQ_INDEX: self.index(),
            API_IAQ_SCORE: self.score,
            API_CO2_VALUE: self.co2,
            API_PM2_5_VALUE: self.pm2_5,
            API_PM10_VALUE: self.pm10,
            API_TVOC_VALUE: self.tvoc,
            API_PRESSURE_VALUE: self.pressure,
        }


class AirzoneIAQ:
    """Airzone Local API IAQ."""

    def __init__(self) -> None:
        """Local API IAQ init."""
        self.sensors: list[AirzoneIAQSensor] = []

    def add_sensor(self, system: int, sensor: int) -> None:
        """Add IAQ Sensor."""
        self.sensors.append(AirzoneIAQSensor(system, sensor))

    async def post(self, request: web.Request) -> Response:
        """POST Local API IAQ."""
        data = await request.json()
        system = data.get(API_SYSTEM_ID) if isinstance(data, dict) else None
        sensor = data.get(API_IAQ_SENSOR_ID) if isinstance(data, dict) else None

        if system is None:
            return api_json_error(API_ERROR_SYSTEM_ID_NOT_PROVIDED)

        sensors = [
            _sensor
            for _sensor in self.sensors
            if system in (0, _sensor.system) and sensor in (0, _sensor.sensor)
        ]
        if not sensors:
            return api_json_error(API_ERROR_IAQ_SENSOR_ID_NOT_AVAILABLE)

        for _sensor in sensors:
            _sensor.refresh()

        if system == 0:
            system_ids = sorted({_sensor.system for _sensor in sensors})
            return api_json_response(
                {
                    API_SYSTEMS: [
                        {
                            API_DATA: [
                                _sensor.data()
                                for _sensor in sensors
                                if _sensor.system == system_id
                            ]
                        }
                        for system_id in system_ids
                    ]
                }
            )
        return api_json_response({API_DATA: [_sensor.data() for _sensor in sensors]})
