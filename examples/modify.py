"""Airzone modify parameters example."""
import asyncio
import json
import time
import timeit

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
            validate_start = timeit.default_timer()
            airzone_mac = await airzone.validate()
            validate_end = timeit.default_timer()
            if airzone_mac is not None:
                print(f"Airzone WebServer: {airzone_mac}")
            print(f"Validate time: {validate_end - validate_start}")
            print("***")

            update_start = timeit.default_timer()
            await airzone.update()
            update_end = timeit.default_timer()
            print(json.dumps(airzone.data(), indent=4, sort_keys=True))
            print(f"Update time: {update_end - update_start}")
            print("***")

            modify_start = timeit.default_timer()
            await airzone.set_hvac_parameters(
                {
                    API_SYSTEM_ID: 1,
                    API_ZONE_ID: 3,
                    API_MODE: 1,
                }
            )
            modify_end = timeit.default_timer()
            print(json.dumps(airzone.data(), indent=4, sort_keys=True))
            print(f"Modify time: {modify_end - modify_start}")
            print("***")

            print("Sleeping...")
            time.sleep(3)
            print("***")

            update_start = timeit.default_timer()
            await airzone.update()
            update_end = timeit.default_timer()
            print(json.dumps(airzone.data(), indent=4, sort_keys=True))
            print(f"Update time: {update_end - update_start}")
        except (ClientConnectorError, InvalidHost):
            print("Invalid host.")


if __name__ == "__main__":
    asyncio.run(main())
