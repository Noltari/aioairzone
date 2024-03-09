"""Airzone loop example."""

import asyncio
import timeit

import _config
import aiohttp
from aiohttp.client_exceptions import ClientConnectorError

from aioairzone.exceptions import InvalidHost
from aioairzone.localapi import AirzoneLocalApi


async def main():
    """Airzone loop example."""

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

            while True:
                update_start = timeit.default_timer()
                tasks = []
                tasks += [airzone.get_webserver()]
                tasks += [airzone.get_hvac_systems()]
                tasks += [airzone.get_hvac()]
                for task in tasks:
                    task_data = await task
                    if task_data is None:
                        print(f"{task}: empty response")
                update_end = timeit.default_timer()
                print(f"Update time: {update_end - update_start}")

        except (ClientConnectorError, InvalidHost) as err:
            print(f"Invalid host: {err}")


if __name__ == "__main__":
    asyncio.run(main())
