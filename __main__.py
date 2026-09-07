import logging
import mimetypes

from core import *
from components import *



logging.basicConfig(level=logging.DEBUG)

router = Router()
html = HTMLTemplateRenderer()


@router.get("/")
async def _(p_request: HTTPRequest) -> HTTPResponse:
    return html.render_file_response("./pages/index.html")


@router.get("/thought/<name>")
async def _(p_request: HTTPRequest, name: str) -> HTTPResponse:
    return html.render_file_response(
            "./pages/thought.html",
            p_title=f"Vanya's thought #{name}",
            p_content=Thought.from_html(f"./thoughts/{name}.html").render_html(),
    )


@router.get("/public/...")
async def _(p_request: HTTPRequest) -> HTTPResponse:
    filesystem_path: str|None = crypto.join_paths_safe("./public", p_request.path.removeprefix("/public"))
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



if __name__ == "__main__":
    pass
    # html.register_components_from_dir("./components")
    # router.serve_until_KeyboardInterrupt("0.0.0.0", 8080, "./certificates/domain.cert.pem", "./certificates/private.key.pem")
