import logging
import mimetypes
import os
import sys

from core import *
from components.image import Image
from components.thought import Thought


logging.basicConfig(level=logging.INFO)

router = Router()
html = HTMLTemplateRenderer()


@router.get("/")
async def _(p_request: HTTPRequest) -> HTTPResponse:
    return html.render_file_response("./pages/index.html")


@router.get("/thought/<name>")
async def _(p_request: HTTPRequest, name: str) -> HTTPResponse:
    return html.render_file_response(
            "./pages/thought.html",
            title=f"Vanya's thought #{name}",
            content=Thought.from_html(f"./thoughts/{name}.html").render_html(),
    )


@router.get("/public/*")
async def _(p_request: HTTPRequest) -> HTTPResponse:
    filesystem_path: str|None = join_paths_safe("./public", p_request.path.removeprefix("/public"))
    if filesystem_path is None:
        return HTTPResponse.reject(b"Path traversing fuck! No!")

    mime_type, _ = mimetypes.guess_type(filesystem_path)
    if mime_type and mime_type.startswith("image") and p_request.query and "w" in p_request.query.keys():
        found_image = Image.from_file(filesystem_path)
        if found_image:
            return HTTPResponse.ok(
                    found_image.resize_and_get_webp_buffer(int(p_request.query.get("w", "0"))),
                    content_type=mime_type
            )
        return HTTPResponse.not_found(b"Image not found")
        
    else:
        return HTTPResponse.ok_file(filesystem_path)


@router.get("/favicon.ico")
async def _(p_request: HTTPRequest) -> HTTPResponse:
    return HTTPResponse.ok_file("./public/favicon.ico")


def serve_forever() -> None:
    html.register_components_from_dir("./components")
    router.serve_until_KeyboardInterrupt("0.0.0.0", 8080, "domain.cert.pem", "private.key.pem")


def test() -> None:
    penetration_test_router(router)


if __name__ == "__main__":
    def pop_arg() -> str|None:
        if sys.argv:
            return sys.argv.pop()
        else:
            return None

    while True:
        token: str|None = pop_arg()
        if token is None:
            break

        match token:
            case "-t":
                test()
                sys.exit(0)
            case _:
                logging.error("Unhandled argument")

        serve_forever()
        sys.exit(0)
