"""Tests for the Airzone Local API client."""

from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from aioairzone.http import AirzoneHttpRequest
from aioairzone.localapi import AirzoneLocalApi, ConnectionOptions


class TestAirzoneLocalApi(IsolatedAsyncioTestCase):
    """Test Airzone Local API requests."""

    def test_http_request_preserves_query_parameters(self) -> None:
        """Preserve query parameters in the compatibility HTTP transport."""
        request = AirzoneHttpRequest(
            "GET",
            "http://airzone.local:3000/api/v1/iaq?systemid=1&iaqsensorid=1",
            {},
        )

        self.assertIn(
            "GET /api/v1/iaq?systemid=1&iaqsensorid=1 HTTP/1.1",
            request.header(),
        )

    async def test_get_iaq_uses_sensor_query_and_stores_raw_response(self) -> None:
        """Fetch AirQ data using the documented query parameters."""
        response = {
            "data": [
                {
                    "systemID": 1,
                    "airqsensorID": 1,
                    "name": "AirQ",
                    "co2_value": 524,
                    "iaq_index": 1,
                    "iaq_score": 96,
                    "pm10_value": 2,
                    "pm2_5_value": 1,
                    "tvoc_value": 147,
                }
            ]
        }
        airzone = AirzoneLocalApi(MagicMock(), ConnectionOptions("airzone.local"))
        airzone.http_request = AsyncMock(return_value=response)

        result = await airzone.get_iaq(system_id=1, iaq_sensor_id=1)

        airzone.http_request.assert_awaited_once_with(
            "GET", "api/v1/iaq?systemid=1&iaqsensorid=1"
        )
        self.assertEqual(result, response)
        self.assertEqual(airzone.raw_data()["iaq"], response)
