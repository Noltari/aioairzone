"""Airzone Local API HTTP implementation."""

import asyncio
from asyncio import Future, Protocol, Transport
import json
from json import JSONDecodeError
import logging
from typing import Any, Final
from urllib.parse import urlparse

from .exceptions import InvalidHost

_LOGGER = logging.getLogger(__name__)


HTTP_EOL: Final[str] = "\r\n"
HTTP_HDR_SEP: Final[str] = f"{HTTP_EOL}{HTTP_EOL}"

HTTP_CHARSET: Final[str] = "charset"
HTTP_CONTENT_LEN: Final[str] = "Content-Length"
HTTP_CONTENT_TYPE: Final[str] = "Content-Type"
HTTP_SERVER: Final[str] = "Server"

HTTP_BUFFER: Final[int] = 4096
HTTP_DEF_TIMEOUT: Final[int] = 30
HTTP_PREFIX: Final[str] = "HTTP"
HTTP_VERSION: Final[str] = "1.1"


class AirzoneHttpRequest:
    """Airzone HTTP request."""

    def __init__(
        self,
        method: str,
        url: str,
        headers: dict[str, Any],
        data: str | None = None,
    ) -> None:
        """HTTP request init."""
        self.data = data
        self.headers = headers
        self.method = method
        self.url = urlparse(url)

    def encode(self) -> bytearray:
        """HTTP request encode."""
        buffer = bytearray(self.header().encode())

        if self.data is not None:
            buffer += self.data.encode()

        return buffer

    def header(self) -> str:
        """HTTP request header."""
        http = f"{self.method} {self.url.path} {HTTP_PREFIX}/{HTTP_VERSION}"
        host = f"Host: {self.url.netloc}"
        headers = ""
        for key, value in self.headers.items():
            headers = f"{headers}{key}: {value}{HTTP_EOL}"
        if self.data is not None:
            headers = f"{headers}Content-Length: {len(self.data)}{HTTP_EOL}"

        return f"{http}{HTTP_EOL}{host}{HTTP_EOL}{headers}{HTTP_EOL}"


class AirzoneHttpResponse:
    """Airzone HTTP response."""

    def __init__(self) -> None:
        """HTTP response init."""
        self.body: str | None = None
        self.buffer = bytearray()
        self.charset: str = "utf-8"
        self.header: str | None = None
        self.header_map: dict[str, str] = {}
        self.media_type: str | None = None
        self.reason: str | None = None
        self.status: int | None = None
        self.version: str | None = None

    def append_data(self, data: bytes) -> None:
        """Buffer HTTP response data."""
        self.buffer += data

    def get_content_length(self) -> int:
        """Get HTTP Content-Length."""
        content_len = self.header_map.get(HTTP_CONTENT_LEN)
        if content_len is not None:
            return int(content_len)
        return 0

    def json(self) -> Any:
        """HTTP response to JSON conversion."""
        if self.body is not None:
            try:
                return json.loads(self.body)
            except JSONDecodeError as err:
                raise InvalidHost(err) from err
        return None

    def parse_content_type(self) -> None:
        """HTTP content type parse."""
        content_type = self.header_map.get(HTTP_CONTENT_TYPE)
        if content_type is None:
            return

        ct_split = content_type.split(";")
        if len(ct_split) < 1:
            return

        self.media_type = ct_split.pop(0).strip().lower()

        charset = None
        for ct_item in ct_split:
            item_split = ct_item.split("=", maxsplit=1)
            if len(item_split) == 2:
                key = item_split[0].strip()
                value = item_split[1].strip()

                if key == HTTP_CHARSET:
                    charset = value.lower()
                    self.charset = charset

        if self.media_type == "text/html" and charset is None:
            self.charset = "iso-8859-1"

    def parse_http_status(
        self,
        status: str,
    ) -> None:
        """HTTP response status parse."""
        if not status.startswith(HTTP_PREFIX):
            return

        status_split = status.strip().split(" ", maxsplit=2)
        self.reason = status_split[2]
        self.status = int(status_split[1])
        self.version = status_split[0].lstrip(f"{HTTP_PREFIX}/")

        _LOGGER.debug(
            "HTTP: version=%s status=%s reason=%s",
            self.version,
            self.status,
            self.reason,
        )

    def parse_header_line(self, line: str) -> None:
        """HTTP response header line parse."""
        line_list = line.split(":", maxsplit=1)
        if len(line_list) == 2:
            key = line_list[0].strip()
            value = line_list[1].strip()

            self.header_map[key] = value

    def parse_header(self) -> None:
        """HTTP response header parse."""
        if self.header is None:
            return

        lines = self.header.splitlines()
        if len(lines) < 1:
            return

        status = lines.pop(0)
        self.parse_http_status(status)

        for line in lines:
            self.parse_header_line(line)

        _LOGGER.debug("HTTP: headers=%s", self.header_map)

        self.parse_content_type()

    def parse_header_bytes(self, header_bytes: bytes) -> None:
        """HTTP response header bytes parse."""
        self.header = header_bytes.decode()
        self.parse_header()

    def parse_body_bytes(self, body_bytes: bytes) -> None:
        """HTTP response body bytes parse."""
        self.body = body_bytes.decode(encoding=self.charset, errors="replace")

        _LOGGER.debug("HTTP: body=%s", self.body)

    def parse_data(self) -> None:
        """Parse HTTP response data."""
        mv = memoryview(self.buffer)

        header_sep_bytes = HTTP_HDR_SEP.encode()
        try:
            header_end = self.buffer.index(header_sep_bytes) + len(header_sep_bytes)
        except ValueError as err:
            raise InvalidHost(
                f"HTTP Header separator not found: {self.buffer}"
            ) from err

        header_bytes = bytes(mv[:header_end])
        self.parse_header_bytes(header_bytes)

        content_len = self.get_content_length()
        if content_len > 0:
            body_end = header_end + content_len
            body_bytes = bytes(mv[header_end:body_end])
            self.parse_body_bytes(body_bytes)


class AirzoneHttpProtocol(Protocol):
    """Airzone HTTP Protocol."""

    def __init__(
        self,
        request: AirzoneHttpRequest,
        response: AirzoneHttpResponse,
        future: Future[Any],
    ) -> None:
        """Airzone HTTP Protocol init."""
        self.future = future
        self.request = request
        self.response = response

    def connection_made(
        self,
        transport: Transport,  # type: ignore
    ) -> None:
        """HTTP connection establised."""
        transport.write(self.request.encode())
        transport.write_eof()

    def connection_lost(self, exc: Exception | None) -> None:
        """HTTP connection lost."""
        if exc is not None:
            _LOGGER.error(exc)

        self.future.set_result(True)

    def data_received(self, data: bytes) -> None:
        """HTTP data received from server."""
        self.response.append_data(data)

    def eof_received(self) -> None:
        """HTTP EOF received from server."""
        self.response.parse_data()


class AirzoneHttp:
    """Airzone HTTP."""

    def __init__(self) -> None:
        """HTTP init."""
        self.headers: dict[str, Any] = {
            "User-Agent": "aioairzone",
            "Accept": "*/*",
        }
        self.loop = asyncio.get_running_loop()

    async def request(
        self,
        method: str,
        url: str,
        data: str | None = None,
        headers: dict[str, Any] | None = None,
        timeout: int = HTTP_DEF_TIMEOUT,
    ) -> AirzoneHttpResponse:
        """HTTP request."""
        async with asyncio.timeout(timeout):
            req_headers = self.headers
            if headers is not None:
                req_headers |= headers

            response = AirzoneHttpResponse()
            request = AirzoneHttpRequest(
                method,
                url,
                headers=req_headers,
                data=data,
            )
            transport = None

            if request.url.hostname is None:
                raise InvalidHost("Invalid URL host.")
            if request.url.port is None:
                raise InvalidHost("Invalid URL port.")

            try:
                future = self.loop.create_future()

                transport, protocol = await self.loop.create_connection(
                    lambda: AirzoneHttpProtocol(request, response, future),
                    request.url.hostname,
                    request.url.port,
                )

                await future
            except OSError as err:
                raise InvalidHost(err) from err
            finally:
                if transport is not None:
                    transport.close()

            return protocol.response
