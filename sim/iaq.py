"""Airzone Local API IAQ sensor."""

from typing import Any

from aiohttp.web_request import Request
from aiohttp.web_response import Response
from helpers import api_json_error, api_json_response

from aioairzone.const import (
    API_DATA,
    API_ERROR_IAQ_SENSOR_ID_NOT_AVAILABLE,
    API_ERROR_SYSTEM_ID_NOT_AVAILABLE,
    API_IAQ_SENSOR_ID,
    API_SYSTEM_ID,
    API_SYSTEM_ID_QUERY,
)


class AirzoneIAQ:
    """Airzone IAQ sensor."""

    def __init__(self) -> None:
        """Initialize IAQ sensor."""
        self.system_id = 1
        self.sensor_id = 1

    def data(self) -> dict[str, Any]:
        """Return Local API IAQ data."""
        return {
            API_SYSTEM_ID: self.system_id,
            "airqsensorID": self.sensor_id,
            "name": "AirQ",
            "iaq_mode_vent": 2,
            "iaq_index": 1,
            "iaq_score": 96,
            "co2_value": 524,
            "pm2_5_value": 1,
            "pm10_value": 2,
            "tvoc_value": 147,
            "pressure_value": 984,
        }

    async def get(self, request: Request) -> Response:
        """GET Local API IAQ sensor data."""
        system_id = request.query.get(API_SYSTEM_ID_QUERY)
        if system_id != str(self.system_id):
            return api_json_error(API_ERROR_SYSTEM_ID_NOT_AVAILABLE)

        sensor_id = request.query.get(API_IAQ_SENSOR_ID)
        if sensor_id != str(self.sensor_id):
            return api_json_error(API_ERROR_IAQ_SENSOR_ID_NOT_AVAILABLE)

        return api_json_response({API_DATA: [self.data()]})
