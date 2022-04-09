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
        client = AirzoneLocalApi(aiohttp_session, _config.AIRZONE_OPTIONS)
        try:
            airzone_mac = await client.validate_airzone()
            if airzone_mac is not None:
                print(f"Airzone WebServer: {airzone_mac}")
            await client.update_airzone()
            print(json.dumps(client.data(), indent=4, sort_keys=True))
        except (ClientConnectorError, InvalidHost):
            print("Invalid host.")


if __name__ == "__main__":
    asyncio.run(main())
