"""Airzone Local API Demo."""

from typing import Any

from aiohttp.web_response import Response
from helpers import api_json_response

from aioairzone.const import API_DATA


class AirzoneDemo:
    """Airzone Local API Demo."""

    def __init__(self) -> None:
        """Local API Demo init."""

    def data(self) -> dict[str, Any]:
        """Return Local API Demo data."""
        return {
            API_DATA: [
                {
                    "systemID": 1,
                    "zoneID": 1,
                    "name": "zona01",
                    "on": 1,
                    "coolsetpoint": 25,
                    "coolmaxtemp": 30,
                    "coolmintemp": 18,
                    "heatsetpoint": 22,
                    "heatmaxtemp": 30,
                    "heatmintemp": 15,
                    "maxTemp": 30,
                    "minTemp": 15,
                    "setpoint": 26,
                    "roomTemp": 20,
                    "modes": [1, 2, 3, 4],
                    "mode": 3,
                    "speeds": 5,
                    "speed": 2,
                    "speed_values": [0, 1, 2, 3, 4, 5],
                    "speed_type": 0,
                    "coldStages": 3,
                    "coldStage": 2,
                    "heatStages": 3,
                    "heatStage": 1,
                    "humidity": 43,
                    "units": 0,
                    "errors": [
                        {"Zone": "Error 3"},
                        {"Zone": "Error 4"},
                        {"Zone": "Error 5"},
                        {"Zone": "Error 6"},
                        {"Zone": "Error 7"},
                        {"Zone": "Error 8"},
                        {"Zone": "Presence alarm"},
                        {"Zone": "Window alarm"},
                        {"Zone": "Anti-freezing alarm"},
                        {"Zone": "Zone without thermostat"},
                        {"Zone": "Low battery"},
                        {"Zone": "Active dew"},
                        {"Zone": "Active dew protection"},
                        {"Zone": "F05-H"},
                        {"Zone": "F06-H"},
                        {"Zone": "F05-C"},
                        {"Zone": "F06-C"},
                        {"system": "Error 9"},
                        {"system": "Error 13"},
                        {"system": "Error 11"},
                        {"system": "Error 15"},
                        {"system": "Error 16"},
                        {"system": "Error C09"},
                        {"system": "Error C11"},
                        {"system": "IU error IU4"},
                        {"system": "Error IAQ1"},
                        {"system": "Error IAQ4"},
                        {"Zone": "Error IAQ2"},
                        {"Zone": "Error IAQ3"},
                    ],
                    "air_demand": 1,
                    "floor_demand": 1,
                    "aq_mode": 2,
                    "aq_quality": 2,
                    "aq_thrlow": 10,
                    "aq_thrhigh": 40,
                    "slats_vertical": 2,
                    "slats_horizontal": 3,
                    "slats_vswing": 1,
                    "slats_hswing": 0,
                    "antifreeze": 1,
                    "eco_adapt": "manual",
                }
            ]
        }

    async def post(self) -> Response:
        """POST Local API Demo."""
        return api_json_response(self.data())
