"""Airzone Local API HTTP implementation."""

import asyncio
import json
from json import JSONDecodeError
import logging
import socket
from typing import Any, Final
from urllib.parse import urlparse

from .exceptions import InvalidHost

_LOGGER = logging.getLogger(__name__)


HTTP_EOL: Final[str] = "\r\n"
HTTP_HDR_SEP: Final[str] = f"{HTTP_EOL}{HTTP_EOL}"

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
        self.body_bytes: bytes | None = None
        self.content_len: int = 0
        self.content_type: str | None = None
        self.header: str | None = None
        self.header_bytes: bytes | None = None
        self.reason: str | None = None
        self.server: str | None = None
        self.status: int | None = None
        self.version: str | None = None

    def is_json(self) -> bool:
        """Check if HTTP content type is JSON."""
        if self.content_type is not None:
            return "json" in self.content_type
        return False

    def json(self) -> Any:
        """HTTP response json."""
        if self.body is not None:
            try:
                return json.loads(self.body)
            except JSONDecodeError as err:
                raise InvalidHost(err) from err
        return None

    def parse_http_status(
        self,
        line: str,
    ) -> None:
        """HTTP response status parse."""
        if not line.startswith(HTTP_PREFIX):
            return

        status_split = line.split(" ", 2)
        self.reason = status_split[2]
        self.status = int(status_split[1])
        self.version = status_split[0].lstrip(f"{HTTP_PREFIX}/")

    def parse_header_line(self, line: str) -> None:
        """HTTP response header line parse."""
        line_list = line.split(":", maxsplit=1)
        if len(line_list) == 2:
            key = line_list[0].strip()
            value = line_list[1].strip()

            _LOGGER.debug("HTTP: %s -> %s", key, value)

            if key == HTTP_CONTENT_LEN:
                self.content_len = int(value)
            elif key == HTTP_CONTENT_TYPE:
                self.content_type = value
            elif key == HTTP_SERVER:
                self.server = value

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

    def parse_header_bytes(self) -> None:
        """HTTP response parse."""
        if self.header_bytes is not None:
            self.header = self.header_bytes.decode()
            self.parse_header()

            _LOGGER.debug(
                "HTTP: version=%s status=%s reason=%s",
                self.version,
                self.status,
                self.reason,
            )

            if not self.is_json():
                raise InvalidHost(f"Invalid HTTP Content-Type: {self.content_type}")

    def parse_body_bytes(self) -> None:
        """HTTP response parse."""
        if self.body_bytes is not None:
            self.body = self.body_bytes.decode()


class AirzoneHttp:
    """Airzone HTTP."""

    def __init__(self) -> None:
        """HTTP init."""
        self.headers: dict[str, Any] = {
            "User-Agent": "aioairzone",
            "Accept": "*/*",
        }

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

            resp = AirzoneHttpResponse()
            req = AirzoneHttpRequest(
                method,
                url,
                headers=req_headers,
                data=data,
            )

            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.connect((req.url.hostname, req.url.port))
                sock.sendall(req.encode())
                sock.shutdown(socket.SHUT_WR)

                buffer = bytearray()
                while True:
                    rx_bytes = sock.recv(HTTP_BUFFER)
                    if rx_bytes == b"":
                        break
                    buffer += rx_bytes
                mv = memoryview(buffer)

                header_sep_bytes = HTTP_HDR_SEP.encode()
                header_end = buffer.index(header_sep_bytes) + len(header_sep_bytes)

                resp.header_bytes = bytes(mv[:header_end])
                resp.parse_header_bytes()

                if resp.content_len > 0:
                    body_end = header_end + resp.content_len
                    resp.body_bytes = bytes(mv[header_end:body_end])
                    resp.parse_body_bytes()

                sock.close()
            except socket.error as err:
                raise InvalidHost(err) from err

            return resp
