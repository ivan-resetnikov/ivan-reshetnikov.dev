import logging
import urllib.parse

from .router import Router


def test(self, p_name: str) -> Callable:

    def definition_wrapper(p_decorated_function: Callable) -> Callable:

        def call_wrapper(*p_args, **p_kwargs) -> str:
            print(f"Running test \"{p_name}\"")
            return p_decorated_function(*p_args, **p_kwargs)

        return call_wrapper

    logging.debug(f"Registered component `{p_name}`")

    return definition_wrapper


@test("Penetration-testing the router")
def penetration_test_router(p_router: Router) -> None:
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

            for candidate in candidates:
                matched = p_router.match(route.method, candidate)

                if matched is not None:
                    assert False, (
                        f"Potential path traversal vulnerability:\n"
                        f"  route:   {route.method} {route_path}\n"
                        f"  payload: {candidate!r}\n"
                        f"  matched: {matched!r}"
                    )

        print("  ✓ passed")