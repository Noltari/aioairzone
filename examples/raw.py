"""Airzone raw API data example."""
import asyncio
import json
import timeit

import _config
import aiohttp
from aiohttp.client_exceptions import ClientConnectorError

from aioairzone.exceptions import InvalidHost
from aioairzone.localapi import AirzoneLocalApi


async def main():
    """Airzone raw API data example."""

    async with aiohttp.ClientSession() as aiohttp_session:
        airzone = AirzoneLocalApi(aiohttp_session, _config.AIRZONE_OPTIONS)
        try:
            validate_start = timeit.default_timer()
            airzone_mac = await airzone.validate()
            validate_end = timeit.default_timer()
            if airzone_mac is not None:
                print(f"Airzone WebServer: {airzone_mac}")
            print(f"Validate time: {validate_end - validate_start}")
            print("***")

            update_start = timeit.default_timer()
            await airzone.get_demo()
            await airzone.get_integration()
            await airzone.get_version()
            await airzone.update()
            update_end = timeit.default_timer()
            print(json.dumps(airzone.data(), indent=4, sort_keys=True))
            print("***")
            print(json.dumps(airzone.raw_data(), indent=4, sort_keys=True))
            print("***")
            print(f"Update time: {update_end - update_start}")
        except (ClientConnectorError, InvalidHost):
            print("Invalid host.")


if __name__ == "__main__":
    asyncio.run(main())
