import mimetypes
from pathlib import Path
from sphinxcontrib.websupport import WebSupport
from .templates import get_dir
from typing import TypedDict, Optional, Union
import jinja2 as j2

j2_env = j2.Environment(loader=j2.FileSystemLoader(get_dir()))

def get_content_type(name):
    content_type = mimetypes.guess_type(name)[0]
    if not content_type:
        if name.endswith(".svg"):
            content_type = "image/svg+xml"
        if name.endswith(".woff"):
            content_type = "application/font-woff"
        if name.endswith(".ttf"):
            content_type = "application/x-font-ttf"
        if name.endswith(".otf"):
            content_type = "application/x-font-ttf"
        if name.endswith(".svgf"):
            content_type = "image/svg+xml"
        if name.endswith(".eot"):
            content_type = "application/vnd.ms-fontobject"
    return content_type

class Response(TypedDict, total=False):
    status: int
    body: Union[str, bytes]
    content_type: str

def handle(
    *, 
    path_str: str, 
    out_dir: str, 
    args: dict[str, str], 
    search_html: str, 
    websupport: WebSupport,
) -> Response:
    out_dir_path = Path(out_dir)

    if path_str == f"/{search_html}":
        q = args.get("q")
        matches = websupport.search.handle_query(q)
        search_body_template = j2_env.get_template("search_body.html")
        search_body = search_body_template.render(
            matches=matches,
        )

        search_html_path = out_dir_path / search_html
        html = search_html_path.read_text(encoding="utf-8")
        html = html.replace(
            "<!-- body_place -->",
            search_body,
        )
        return {
            "status": 200,
            "body": html,
        }

    else:
        path = (out_dir_path / path_str.lstrip("/")).resolve()
        if path.exists():
            return {
                "status": 200,
                "body": path.read_bytes(),
                "content_type": get_content_type(path.name),
            }
        else:
            return {
                "status": 404,
            }
