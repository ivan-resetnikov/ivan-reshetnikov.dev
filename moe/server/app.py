import logging
import asyncio
import inspect

from .http import HTTPServer, HTTPRequest, HTTPResponse
from .html import HTMLRenderer, HTML

from collections.abc import Callable



Error = str



class Route:
    def __init__(self, p_method: str, p_path: str, p_handler: Callable) -> None:
        self.method: str = p_method
        self.path: str = p_path
        self.handler: Callable = p_handler



class App:
    logger: logging.Logger = logging.getLogger("App")
    logger.setLevel(logging.DEBUG)
    
    def __init__(self) -> None:
        # NOTE(vanya): The two must be in sync
        self.routes: list[Route] = []
        self.method_routes: dict[str, list[Route]] = {}

        self.public_prefix: str = ""
        self.public_handler: Callable = None

        self.http_server: HTTPServer = None
        self.html_renderer: HTMLRenderer = HTMLRenderer()

    
    def get(self, p_route: str) -> Callable:

        def definition_wrapper(p_decorated_function: Callable) -> Callable:

            async def call_wrapper(p_request_info: HTTPRequest) -> HTTPResponse:
                if inspect.iscoroutinefunction(p_decorated_function):
                    return await p_decorated_function(p_request_info)
                else:
                    return p_decorated_function(p_request_info)

            self.register_route("GET", p_route, call_wrapper)

            return call_wrapper

        return definition_wrapper


    def post(self, p_route: str) -> Callable:

        def definition_wrapper(p_decorated_function: Callable) -> Callable:
            
            async def call_wrapper(p_request_info: HTTPRequest) -> HTTPResponse:
                if inspect.iscoroutinefunction(p_decorated_function):
                    return await p_decorated_function(p_request_info)
                else:
                    return p_decorated_function(p_request_info)

            self.register_route("POST", p_route, call_wrapper)

            return call_wrapper

        return definition_wrapper
    

    def public(self, p_prefix: str) -> Callable:

        def definition_wrapper(p_decorated_function: Callable) -> Callable:
            
            async def call_wrapper(p_request_info: HTTPRequest) -> HTTPResponse:
                if inspect.iscoroutinefunction(p_decorated_function):
                    return await p_decorated_function(p_request_info)
                else:
                    return p_decorated_function(p_request_info)

            self.public_prefix = p_prefix
            self.public_handler = call_wrapper

            return call_wrapper

        return definition_wrapper
    

    def register_route(self, p_method: str, p_path: str, p_handler: Callable) -> None:
        new_route = Route(p_method, p_path, p_handler)

        self.logger.debug(f"Registering route `{p_method} {p_path}`")

        self.routes.append(new_route)
        self.method_routes[p_method] = self.method_routes.get(p_method, []) + [new_route]


    def serve_until_KeyboardInterrupt(self, p_port: int = 8000) -> Error:
        self.http_server = HTTPServer()
        
        try:
            return asyncio.run(self.http_server.serve_forever(self.handle_http_request, p_port))
        
        except KeyboardInterrupt:
            self.logger.info("Received KeyboardInterrupt, closing server")
            return "OK"
    

    async def handle_http_request(self, p_request: HTTPRequest) -> bytes:
        self.logger.debug(f"Handling HTTP request `{p_request.method} {p_request.path}`")

        if (
            p_request.method == "GET"
            and self.public_handler
            and p_request.path.startswith(self.public_prefix)
        ):
            self.logger.debug(
                f"Using public handler for path `{p_request.path}`"
            )
            return await self.public_handler(p_request)

        method_routes: list[Route] = self.method_routes.get(
            p_request.method,
            []
        )

        request_path = p_request.path
        if "?" in request_path:
            request_path = request_path.split("?", 1)[0]

        request_parts: list[str] = request_path.strip("/").split("/")

        for route in method_routes:
            route_parts: list[str] = route.path.strip("/").split("/")

            params: dict[str, str] = {}

            route_index: int = 0
            request_index: int = 0

            matched: bool = True

            while route_index < len(route_parts):
                route_part: str = route_parts[route_index]

                # NOTE(vanya): Catchall
                if route_part.startswith("[...") and route_part.endswith("]"):
                    key: str = route_part[4:-1]

                    params[key] = "/".join(
                        request_parts[request_index:]
                    )

                    request_index = len(request_parts)
                    route_index = len(route_parts)

                    break

                # NOTE(vanya): Request shorter than route
                if request_index >= len(request_parts):
                    matched = False
                    break

                request_part: str = request_parts[request_index]

                # NOTE(vanya): Param
                if route_part.startswith("[") and route_part.endswith("]"):
                    key: str = route_part[1:-1]
                    params[key] = request_part

                # NOTE(vanya): Static path
                elif route_part != request_part:
                    matched = False
                    break

                route_index += 1
                request_index += 1

            # NOTE(vanya): Extra unmatched request parts
            if (
                matched
                and request_index != len(request_parts)
                and route_index != len(route_parts)
            ):
                matched = False

            if not matched:
                continue

            p_request.catchall.update(params)

            self.logger.debug(f"Using route `{route.path}`")

            # NOTE(vanya): Parse cookies
            for header_line in p_request.headers:
                if header_line.startswith("Cookie: "):
                    cookie_line: str = header_line.split(": ", 1)[1]

                    if "=" in cookie_line:
                        key, value = cookie_line.split("=", 1)
                        p_request.cookies[key] = value

            return await route.handler(p_request)

        self.logger.debug("Route not found, returning 404")
        return HTTPResponse.not_found()