"""Basic Airzone client example."""
import asyncio
import json

import _config
import aiohttp
from aiohttp.client_exceptions import ClientConnectorError

from aioairzone.exceptions import InvalidHost
from aioairzone.localapi import AirzoneLocalApi


async def main():
    """Basic Airzone client example."""

    async with aiohttp.ClientSession() as aiohttp_session:
        airzone = AirzoneLocalApi(aiohttp_session, _config.AIRZONE_OPTIONS)
        try:
            airzone_mac = await airzone.validate()
            if airzone_mac is not None:
                print(f"Airzone WebServer: {airzone_mac}")
            await airzone.update()
            print(json.dumps(airzone.data(), indent=4, sort_keys=True))
        except (ClientConnectorError, InvalidHost):
            print("Invalid host.")


if __name__ == "__main__":
    asyncio.run(main())
