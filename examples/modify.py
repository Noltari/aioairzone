"""Airzone modify parameters example."""
import asyncio
import json
import time

import _config
import aiohttp
from aiohttp.client_exceptions import ClientConnectorError

from aioairzone.const import API_MODE, API_SYSTEM_ID, API_ZONE_ID
from aioairzone.exceptions import InvalidHost
from aioairzone.localapi import AirzoneLocalApi


async def main():
    """Airzone modify parameters example."""

    async with aiohttp.ClientSession() as aiohttp_session:
        airzone = AirzoneLocalApi(aiohttp_session, _config.AIRZONE_OPTIONS)
        try:
            airzone_mac = await airzone.validate()
            if airzone_mac is not None:
                print(f"Airzone WebServer: {airzone_mac}")
            await airzone.update()
            print(json.dumps(airzone.data(), indent=4, sort_keys=True))
            print("***")

            await airzone.set_hvac_parameters(
                {
                    API_SYSTEM_ID: 1,
                    API_ZONE_ID: 3,
                    API_MODE: 1,
                }
            )
            print(json.dumps(airzone.data(), indent=4, sort_keys=True))
            print("***")

            time.sleep(3)
            await airzone.update()
            print(json.dumps(airzone.data(), indent=4, sort_keys=True))
        except (ClientConnectorError, InvalidHost):
            print("Invalid host.")


if __name__ == "__main__":
    asyncio.run(main())
