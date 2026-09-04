import logging
import urllib.parse

from collections.abc import Callable

from core import *


def testthing(p_name: str) -> Callable:

    def definition_wrapper(p_decorated_function: Callable) -> Callable:
        def call_wrapper(*p_args, **p_kwargs) -> None:
            logging.info(f"Running test \"{p_name}\"")
            p_decorated_function(*p_args, **p_kwargs)
            logging.info(f"Test passed")

        return call_wrapper

    logging.debug(f"Registered component `{p_name}`")

    return definition_wrapper


@testthing("Penetration-testing the router")
def penetrate_router(p_router: Router) -> None:
    """
    Run a path-traversal test against routes that try to navigate up the file system tree.

    Raises AssertionError when a suspicious payload is accepted in a way that changes the route unexpectedly.
    """

    TRAVERSAL_PAYLOADS = (
        "../",
        "../../",
        "../../../",
        "..%2f",
        "%2e%2e/",
        "%2e%2e%2f",
        "..%5c",
        "%2e%2e%5c",
        "....//",
        "....\\\\",
    )


    for route in p_router.routes:
        route_path = route.path

        # Only test routes that accept a path parameter.
        if "<path>" not in route_path:
            continue

        logging.info(f"Requesting {route.method} {route_path}")

        for payload in TRAVERSAL_PAYLOADS:
            test_path = route_path.replace("<path>", payload)

            # NOTE(vanya): Test both raw and URL-encoded variants.
            candidates: set[str] = {
                test_path,
                urllib.parse.quote(test_path),
            }

            for candidate_path in candidates:
                malitious_request = HTTPRequest()
                malitious_request.method = route.method
                malitious_request.url = candidate_path
        
                malitious_request.path = candidate_path
        
                malitious_request.body = b""

                response = p_router.HTTP_request_handler(malitious_request)

                if response == 200:
                    assert False, (
                        f"Potential path traversal vulnerability found!:\n"
                        f"  route:   {route.method} {route_path}\n"
                        f"  payload: {candidate_path!r}\n"
                        f"  matched: {matched!r}"
                    )
