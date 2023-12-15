"""Airzone Local API Helpers."""

from collections.abc import Mapping
import json
from typing import Any

from aiohttp import web
from aiohttp.web_response import Response

from aioairzone.const import API_ERROR, API_ERRORS


def api_error_dict(error: str) -> dict[str, Any]:
    """Local API error dict."""
    return {
        API_ERRORS: [
            {
                API_ERROR: error,
            },
        ],
    }


def api_filter_dict(data: Any, keep: list[str]) -> Any:
    """Local API dict filter."""

    if not isinstance(data, (Mapping, list)):
        return data

    if isinstance(data, list):
        return [api_filter_dict(val, keep) for val in data]

    filtered = {**data}

    keys = list(filtered)
    for key in keys:
        if key not in keep:
            filtered.pop(key)
        elif isinstance(filtered[key], Mapping):
            filtered[key] = api_filter_dict(filtered[key], keep)
        elif isinstance(filtered[key], list):
            filtered[key] = [api_filter_dict(item, keep) for item in filtered[key]]

    return filtered


def api_json_dumps(obj: Any) -> Any:
    """Local API JSON dumps."""
    return json.dumps(obj, indent=4, sort_keys=False)


def api_json_error(error: str) -> Response:
    """Local API error."""
    return api_json_response(api_error_dict(error))


def api_json_response(data: dict[str, Any]) -> Response:
    """Return Local API error."""
    return web.json_response(data, dumps=api_json_dumps)


def celsius_to_fahrenheit(celsius: float | int) -> float | int:
    """Convert Celsius to Fahrenheit."""
    fahrenheit = (celsius * 9 / 5) + 32
    if isinstance(celsius, float):
        return fahrenheit
    return int(fahrenheit)
