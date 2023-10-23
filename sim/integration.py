"""Airzone Local API Integration."""

from typing import Any

from aiohttp import web
from aiohttp.web_response import Response
from helpers import api_filter_dict, api_json_response

from aioairzone.const import API_DRIVER, API_SYSTEM_ID


class AirzoneIntegration:
    """Airzone Local API Integration."""

    def __init__(self, driver: str) -> None:
        """Local API Integration init."""
        self.driver: str = driver

    def data(self) -> dict[str, Any]:
        """Return Local API Integration data."""
        return {
            API_DRIVER: self.driver,
        }

    async def post(self, request: web.Request) -> Response:
        # pylint: disable=unused-argument
        """POST Local API Integration."""
        return api_json_response(self.data())

    async def put(self, request: web.Request) -> Response:
        """PUT Local API Integration."""
        data = await request.json()
        if isinstance(data, dict):
            keys = list(data) + [API_SYSTEM_ID]

            driver = data.get(API_DRIVER)
            if driver is not None:
                self.driver = data[API_DRIVER]

            return api_json_response(api_filter_dict(self.data(), keys))

        return api_json_response(self.data())
