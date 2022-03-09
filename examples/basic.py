"""Basic Airzone client example."""
import asyncio
import json
import time

import aiohttp
from aiohttp.client_exceptions import ClientConnectorError

from aioairzone.common import ConnectionOptions
from aioairzone.const import API_MODE, API_SYSTEM_ID, API_ZONE_ID
from aioairzone.exceptions import InvalidHost
from aioairzone.localapi_device import AirzoneLocalApi


async def main():
    """Basic Airzone client example."""

    options = ConnectionOptions("192.168.1.25", 3000)
    async with aiohttp.ClientSession() as aiohttp_session:
        client = AirzoneLocalApi(aiohttp_session, options)
        try:
            await client.validate_airzone()
            await client.update_airzone()
            print(json.dumps(client.data(), indent=4, sort_keys=True))

            await client.put_hvac(
                {
                    API_SYSTEM_ID: 1,
                    API_ZONE_ID: 3,
                    API_MODE: 1,
                }
            )
            time.sleep(3)
            await client.update_airzone()
            print(json.dumps(client.data(), indent=4, sort_keys=True))
        except (ClientConnectorError, InvalidHost):
            print("Invalid host.")


if __name__ == "__main__":
    asyncio.run(main())
