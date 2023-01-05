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
from .handle import handle


def preview(
    *,
    out: str,
    support: str,
    aws_host: str,
    aws_region: str,
    es_index_name: str,
    search_html: str,
):
    out_dir_path = Path(out)
    search_html_path = out_dir_path / search_html

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

    @app.route("/<path:path_str>")
    def _handle(path_str):
        ret = handle(
            path_str=request.path,
            out_dir=out,
            args=request.args,
            search_html=search_html,
            websupport=websupport,
        )

        if ret["status"] != 200 and "body" not in ret:
            abort(ret["status"])
        else:
            resp = Response(
                status=ret.get("status", 200),
                response=ret.get("body", None),
                content_type=ret.get("content_type", None),
            )
            return resp

    app.debug = True
    app.run(host="0.0.0.0")
