from __future__ import annotations

import asyncio
import errno
import mimetypes
import os
import ssl
import logging

from collections.abc import Awaitable, Callable
import traceback

import urllib.parse



Error = str



class HTTPRequest:
    def __init__(self) -> None:
        self.method: str = ""
        self.url: str = ""
        self.http_version: str = ""

        self.scheme: str = ""
        self.domain: str = ""
        self.path: str = ""
        self.query: dict[str, str]|None = None
        self.fragment: str|None = None
        self.username: str|None = None
        self.password: str|None = None
        self.hostname: str|None = None
        self.port: int|None = None

        self.headers: list[str] = []
        self.headers_dict: dict[str, str] = {}
        self.body: bytes = b""

        self.cookies: dict[str, str] = {}
        self.catchall: dict[str, str] = {}

        # NOTE(vanya): Sorted by preference, user's most preffered language first
        self.preffered_languages: list[str] = []




class HTTPResponse:
    def __init__(self) -> None:
        self.status_code: int = 200
        self.headers: list[str] = []
        self.body: bytes = b""
        self.content_type: str = "text/plain; charset=utf-8"


    def to_bytes(self) -> bytes:
        header_str = "\r\n".join([
            f"HTTP/1.1 {self.status_code}",
            f"Content-Type: {self.content_type}",
            f"Content-Length: {len(self.body)}",
            *self.headers,
        ])
        return header_str.encode("utf-8") + b"\r\n\r\n" + self.body


    @classmethod
    def ok(cls, p_data: bytes = b"", content_type: str = "text/plain; charset=utf-8") -> HTTPResponse:
        new_response = cls()
        new_response.status_code = 200
        new_response.body = p_data
        new_response.content_type = content_type
        return new_response


    @classmethod
    def server_error(cls, p_data: bytes = b"", content_type: str = "text/plain; charset=utf-8") -> HTTPResponse:
        new_response = cls()
        new_response.status_code = 500
        new_response.body = p_data
        new_response.content_type = content_type
        return new_response


    @classmethod
    def not_found(cls, p_data: bytes = b"", content_type: str = "text/plain; charset=utf-8") -> HTTPResponse:
        new_response = cls()
        new_response.status_code = 404
        new_response.body = p_data
        new_response.content_type = content_type
        return new_response


    @classmethod
    def reject(cls, p_data: bytes = b"", content_type: str = "text/plain; charset=utf-8") -> HTTPResponse:
        new_response = cls()
        new_response.status_code = 403
        new_response.body = p_data
        new_response.content_type = content_type
        return new_response


    @classmethod
    def redirect(cls, p_new_url: str, p_data: bytes = b"", content_type: str = "text/plain; charset=utf-8") -> HTTPResponse:
        new_response = cls()
        new_response.status_code = 302
        new_response.headers.append(f"Location: {p_new_url}")
        new_response.body = p_data
        new_response.content_type = content_type
        return new_response


    @classmethod
    def ok_file(cls, p_path: str) -> HTTPResponse:
        if os.path.exists(p_path) and os.path.isfile(p_path):
            mime_type, _ = mimetypes.guess_type(p_path)
            mime_type = mime_type or "application/octet-stream"

            with open(p_path, "rb") as f:
                return HTTPResponse.ok(f.read(), content_type=mime_type)

        return HTTPResponse.not_found()


HTTPRequestHandlerType = Callable[[HTTPRequest], Awaitable[HTTPResponse]]


class HTTPServer:
    def __init__(self) -> None:
        self.request_handler: HTTPRequestHandlerType|None = None

    
    async def serve_forever(
            self,
            p_HTTP_request_handler: HTTPRequestHandlerType,
            p_ip: str="127.0.0.1",
            p_port: int=8000,
            p_tls_cert_file: str|None=None,
            p_tls_key_file: str|None=None,
    ) -> Error:
        self.request_handler = p_HTTP_request_handler
        
        try:
            ssl_context: ssl.SSLContext|None = None

            if p_tls_cert_file is not None and p_tls_key_file is not None:
                logging.info("TLS certificate & key were provided! Proceeding with SSL.")

                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

                ssl_context.load_cert_chain(
                    certfile=p_tls_cert_file,
                    keyfile=p_tls_key_file,
                )

            server = await asyncio.start_server(
                self.on_HTTP_client_connected,
                p_ip,
                p_port,
                ssl=ssl_context,
            )

            logging.info(f"Server up at `http://{p_ip}:{p_port}` (Press Ctrl+C to stop)")

            async with server:
                await server.serve_forever()

        except OSError as error:
            match error.errno:
                case errno.EADDRINUSE:
                    logging.error(f"OSError .errno=EADDRINUSE ({error.errno}) - Port already in use.")
                case errno.EACCES:
                    logging.error(f"OSError .errno=EACCES ({error.errno}) - Permission denied by the OS.")
                case errno.EINVAL:
                    logging.error(f"OSError .errno=EINVAL ({error.errno}) - Invalid address.")
                case errno.EAFNOSUPPORT:
                    logging.error(f"OSError .errno=EAFNOSUPPORT ({error.errno}) - Address family not supported.")
                case errno.EADDRNOTAVAIL:
                    logging.error(f"OSError .errno=EADDRNOTAVAIL ({error.errno}) - Trying to bind to an IP not assigned to your machine.")
                case errno.EOPNOTSUPP:
                    logging.error(f"OSError .errno=EOPNOTSUPP ({error.errno}) - Binding not supported by the OS.")
                case _:
                    logging.error(f"OSError .errno=UNKNOWN ({error.errno}) - Unhandled error had occured!")
            return "SERVER_START_FAIL"
        
        except Exception as e:
            logging.error(f"Server error: {e}")
            return "SERVER_ERROR"
        
        return "OK"


    async def on_HTTP_client_connected(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        assert self.request_handler

        try:
            logging.debug(f"New client at `{writer.get_extra_info('peername')}`")

            # NOTE(vanya): HTTPRequest is a bundle of all the data of the HTTP request.
            request = HTTPRequest()
            
            # NOTE(vanya): Recieve request line
            request_line_bytes: bytes = await reader.readline()
            if not request_line_bytes:
                return

            request_line: str = request_line_bytes.decode("utf-8")
            request_line_parts: list[str] = request_line.split(" ", 2)

            request.method = request_line_parts[0]
            request.url = request_line_parts[1]
            request.http_version = request_line_parts[2].strip() # NOTE(vanya): Remove trailing \r\n

            logging.debug(f"Received request `{request.method} {request.url} {request.http_version}`")

            url_parts = urllib.parse.urlsplit(request.url)
            request.scheme = url_parts.scheme
            request.domain = url_parts.netloc
            request.path = url_parts.path
            request.query = dict(urllib.parse.parse_qsl(url_parts.query)) if url_parts.query else None
            request.fragment = url_parts.fragment
            request.username = url_parts.username
            request.password = url_parts.password
            request.hostname = url_parts.hostname
            request.port = url_parts.port

            # NOTE(vanya): Recieve headers
            while True:
                header = await reader.readline()
                if header == b'\r\n' or header == b'\n' or not header:
                    # NOTE(vanya): End of headers
                    break
                else:
                    # NOTE(vanya): Store raw AND parsed header
                    header_str: str = header.decode("utf-8").rstrip("\r\n")
                    request.headers.append(header_str)

                    header_parts: list[str] = header_str.split(": ", 2)
                    request.headers_dict[header_parts[0]] = header_parts[1]

            # NOTE(vanya): Receive body
            content_length = int(request.headers_dict.get("Content-Length", "0"))

            request.body = b""
            if content_length > 0:
                request.body = await reader.readexactly(content_length)

            # NOTE(vanya): Get response from request handler
            response: HTTPResponse = await self.request_handler(request)

            # NOTE(vanya): Send response
            writer.write(response.to_bytes())
            await writer.drain()

        except Exception as e:
            logging.error(f"An error occured while handling the request above!")
            logging.error("CALL STACK BEGIN".center(50, "-"))
            traceback.print_exc()
            logging.error("CALL STACK END".center(50, "-"))
            logging.info(f"Responding with a server error.")

            writer.write(HTTPResponse().server_error(b"Server error").to_bytes())
            await writer.drain()
        
        finally:
            logging.debug(f"Closing client connection")
            writer.close()
            await writer.wait_closed()
