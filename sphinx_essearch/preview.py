import mimetypes
from pathlib import Path

from flask import (
    Flask,
    Response,
    abort,
    render_template,
    request,
)
from sphinx.util.console import nocolor
from sphinxcontrib.websupport import WebSupport

from .search import ESSearch
from .templates import get_dir


def preview(
    *,
    out: str,
    support: str,
    aws_host: str,
    aws_region: str,
    es_index_name: str,
):
    out_dir_path = Path(out)
    search_html_path = out_dir_path / "search.html"

    app = Flask(__name__)
    app.template_folder = get_dir()
    websupport = WebSupport(
        builddir=support,
        search=ESSearch(
            aws_host=aws_host,
            aws_region=aws_region,
            index_name=es_index_name,
        ),
    )

    nocolor()

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

    @app.route("/<path:path_str>")
    def get_file(path_str):
        path = (out_dir_path / path_str).resolve()
        if path.exists():
            return Response(
                response=path.read_bytes(),
                content_type=get_content_type(path.name),
            )
        else:
            abort(404)

    @app.route("/search.html")
    def search():
        q = request.args.get("q")
        matches = websupport.search.handle_query(q)
        search_body = render_template(
            "search_body.html",
            matches=matches,
        )

        html = search_html_path.read_text(encoding="utf-8")
        html = html.replace(
            "<!-- body_place -->",
            search_body,
        )
        return Response(
            response=html,
        )

    app.debug = True
    app.run(host="0.0.0.0")
