import asyncio
import logging

from collections.abc import Callable
from fnmatch import fnmatch

from .http import HTTPServer, HTTPRequest, HTTPResponse, HTTPRequestHandlerType



Error = str



class Route:
    def __init__(self, p_method: str, p_path: str, p_handler: Callable) -> None:
        self.method: str = p_method
        self.path: str = p_path
        self.callback: HTTPRequestHandlerType = p_handler



class Router:
    """
    An HTTP request handler.
    It works by matching and calling back different functions that are @decorated to act like endpoints.
    """

    def __init__(self) -> None:
        # WARNING(vanya): The two varaibles below must be in sync
        self.routes: list[Route] = []
        self.method_routes: dict[str, list[Route]] = {}

        self.public_prefix: str = ""
        self.public_handler: Callable|None = None


    def get(self, p_route: str) -> Callable:

        def definition_wrapper(p_decorated_function: HTTPRequestHandlerType) -> Callable:

            async def call_wrapper(p_request_info: HTTPRequest, **p_kwargs: dict) -> HTTPResponse:
                return await p_decorated_function(p_request_info, **p_kwargs)

            self.register_route("GET", p_route, call_wrapper)

            return call_wrapper

        return definition_wrapper


    def register_route(self, p_method: str, p_path: str, p_handler: HTTPRequestHandlerType) -> None:
        new_route = Route(p_method, p_path, p_handler)

        logging.debug(f"Registering route `{p_method} {p_path}`")

        self.routes.append(new_route)
        self.method_routes[p_method] = self.method_routes.get(p_method, []) + [new_route]


    def serve_until_KeyboardInterrupt(
            self,
            p_ip: str="127.0.0.1",
            p_port: int=8000,
            p_tls_cert_file: str|None=None,
            p_tls_key_file: str|None=None,
    ) -> Error:
        self.http_server = HTTPServer()

        try:
            return asyncio.run(self.http_server.serve_forever(self.HTTP_request_handler, p_ip, p_port, p_tls_cert_file, p_tls_key_file))
        
        except KeyboardInterrupt:
            logging.info("Received KeyboardInterrupt, closing server.")
            return "OK"


    async def HTTP_request_handler(self, p_request: HTTPRequest) -> HTTPResponse:
        for route in self.method_routes.get(p_request.method, []):
            route_parts = route.path.strip("/").split("/")
            request_parts = p_request.path.strip("/").split("/")

            if len(request_parts) < len(route_parts):
                continue

            route_args: dict[str, str] = {}
            matched: bool = True

            for i, route_part in enumerate(route_parts):
                request_part = request_parts[i]

                if route_part == "*":
                    # Wildcard matches everything remaining
                    break

                if route_part.startswith("<") and route_part.endswith(">"):
                    argument_name = route_part[1:-1]
                    route_args[argument_name] = request_part
                    continue

                if route_part != request_part:
                    matched = False
                    break

            if not matched:
                logging.debug(f"Route {route.path} rejected.")
                continue

            logging.debug(f"Route {route.path} matched with requested path {p_request.path}")

            return await route.callback(p_request, **route_args)

        return HTTPResponse.not_found(
            "404".encode("utf-8"),
            "text/html; charset=utf-8"
        )
