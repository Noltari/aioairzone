"""Airzone Local API simulation."""

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from demo import AirzoneDemo
from helpers import api_json_error
from hvac import AirzoneACSStatus, AirzoneHVAC
from integration import AirzoneIntegration
from version import AirzoneVersion
from webserver import AirzoneWebServer

from aioairzone.common import TemperatureUnit
from aioairzone.const import API_ERROR_METHOD_NOT_SUPPORTED, API_V1, DEFAULT_PORT

# Airzone device simulation


class Airzone:
    """Airzone Local API."""

    def __init__(self) -> None:
        """Local API Version init."""
        self.demo: AirzoneDemo = AirzoneDemo()
        self.hvac: AirzoneHVAC = AirzoneHVAC()
        self.integration: AirzoneIntegration = AirzoneIntegration("driver")
        self.version: AirzoneVersion = AirzoneVersion("1.64")
        self.webserver: AirzoneWebServer = AirzoneWebServer("11:22:33:44:55:66")


airzone = Airzone()
airzone.hvac.add_zone("", 1, 1, TemperatureUnit.CELSIUS)
airzone.hvac.acs.set_status(AirzoneACSStatus.ENABLED)

# Airzone Local API simulation

routes = web.RouteTableDef()


@routes.post(f"/{API_V1}/demo")
async def demo_post_handler(request: Request) -> Response:
    # pylint: disable=unused-argument
    """POST /demo."""
    return await airzone.demo.post()


@routes.post(f"/{API_V1}/hvac")
async def hvac_post_handler(request: Request) -> Response:
    """POST /hvac."""
    return await airzone.hvac.post(request)


@routes.put(f"/{API_V1}/hvac")
async def hvac_put_handler(request: Request) -> Response:
    """PUT /hvac."""
    return await airzone.hvac.put(request)


@routes.post(f"/{API_V1}/integration")
async def integration_post_handler(request: Request) -> Response:
    """POST /integration."""
    return await airzone.integration.post(request)


@routes.put(f"/{API_V1}/integration")
async def integration_put_handler(request: Request) -> Response:
    """PUT /integration."""
    return await airzone.integration.put(request)


@routes.post(f"/{API_V1}/version")
async def version_post_handler(request: Request) -> Response:
    # pylint: disable=unused-argument
    """POST /version."""
    return await airzone.version.post()


@routes.post(f"/{API_V1}/webserver")
async def webserver_post_handler(request: Request) -> Response:
    # pylint: disable=unused-argument
    """POST /webserver."""
    return await airzone.webserver.post()


@routes.get("/{tail:.*}")
async def root_get_handler(request: Request) -> Response:
    """GET root."""
    # pylint: disable=unused-argument
    raise web.HTTPInternalServerError()


@routes.post("/{tail:.*}")
async def root_post_handler(request: Request) -> Response:
    # pylint: disable=unused-argument
    """POST root."""
    return api_json_error(API_ERROR_METHOD_NOT_SUPPORTED)


@routes.put("/{tail:.*}")
async def root_put_handler(request: Request) -> Response:
    # pylint: disable=unused-argument
    """PUT root."""
    return api_json_error(API_ERROR_METHOD_NOT_SUPPORTED)


app = web.Application()
app.add_routes(routes)
web.run_app(app, port=DEFAULT_PORT)
