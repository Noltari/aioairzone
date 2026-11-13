"""Airzone MQTT basic example."""

import asyncio
import json
import timeit

import _config
from _secrets import MQTT_TOPIC
import aiohttp
from aiohttp.client_exceptions import ClientConnectorError
from mqtt import AirzoneMqttHelper

from aioairzone.exceptions import InvalidHost
from aioairzone.localapi import AirzoneLocalApi
from aioairzone.mqtt import AirzoneMqttUpdate


async def main() -> None:
    """Airzone MQTT example."""

    airzone: AirzoneLocalApi

    async def mqtt_update_callback(update: AirzoneMqttUpdate) -> None:
        """MQTT update callback function."""
        await airzone.mqtt_update(update)

    mqtt_helper = AirzoneMqttHelper()
    mqtt_helper.msg_callback = mqtt_update_callback

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
        except (ClientConnectorError, InvalidHost) as err:
            print(f"Invalid host: {err}")
    print("***")

    mqtt_helper.connect_helper()
    mqtt_helper.subscribe_helper()
    topic, payload = airzone.mqtt.cmd_get_status(MQTT_TOPIC)
    await mqtt_helper.publish(
        topic=topic,
        payload=json.dumps(payload),
        qos=1,
    )
    print("***")

    print("Sleeping...")
    await asyncio.sleep(60)
    print("***")

    print(json.dumps(airzone.data(), indent=4, sort_keys=True))
    print("***")
    print(json.dumps(airzone.raw_data(), indent=4, sort_keys=True))
    print("***")

    mqtt_helper.disconnect_helper()


if __name__ == "__main__":
    asyncio.run(main())
