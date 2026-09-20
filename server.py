import json
import logging
import mimetypes
import hashlib
import hmac

from core import *
from components import *




GITHUB_WEBHOOK_SECRET: str = ""


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


@router.post("/github-webhook")
async def _(p_request: HTTPRequest) -> HTTPResponse:
    payload: dict = json.loads(p_request.body)

    signature: str|None = p_request.headers_dict.get("X-Hub-Signature-256")
    expected: str = "sha256=" + hmac.new(
        GITHUB_WEBHOOK_SECRET,
        p_request.body,
        hashlib.sha256,
    ).hexdigest()

    if not signature or not hmac.compare_digest(signature, expected):
        ip_blacklist.add(p_request.ip)
        return HTTPResponse.reject(b"Fuck off you impersonating fuck!")

    # NOTE(vanya): Mark current version as invalid to the supervisor by creating a file .out_of_date
    with open(".out_of_date", "w") as f:
        f.write("")

    return HTTPResponse.ok()


@router.get("/favicon.ico")
async def _(p_request: HTTPRequest) -> HTTPResponse:
    return HTTPResponse.ok_file("./public/favicon.ico")


@router.middleware()
def _(p_request: HTTPRequest) -> bool:
    if ip_blacklist.contains(p_request.ip):
        return False

    return True



if __name__ == "__main__":
    ip_blacklist.load("./ip_blacklist.txt")
    html.register_components_from_dir("./components")
    router.serve_until_KeyboardInterrupt("0.0.0.0", 8080, "./certificates/domain.cert.pem", "./certificates/private.key.pem")
