"""Airzone Local API Version."""

from typing import Any

from aiohttp.web_response import Response
from helpers import api_json_response

from aioairzone.const import API_VERSION


class AirzoneVersion:
    """Airzone Local API Version."""

    def __init__(self, version: str) -> None:
        """Local API Version init."""
        self.version: str = version

    def data(self) -> dict[str, Any]:
        """Return Local API Version data."""
        return {
            API_VERSION: self.version,
        }

    async def post(self) -> Response:
        """POST Local API version."""
        return api_json_response(self.data())
