from flask import (
    Flask,
    Response,
    abort,
    request,
)
from sphinx.util.console import nocolor

from .handler.fs_handler import FSHandler
from .search import ESSearch


def preview(
    *,
    out: str,
    aws_host: str,
    aws_region: str,
    es_index_name: str,
    search_html: str,
):
    app = Flask(__name__)
    search = ESSearch(
        aws_host=aws_host,
        aws_region=aws_region,
        index_name=es_index_name,
    )
    handler = FSHandler(
        out=out,
        search=search,
        search_html=search_html,
    )

    nocolor()

    @app.route("/<path:path_str>")
    def _handle(path_str):
        ret = handler.handle(
            path_str=request.path,
            args=request.args,
        )

        if ret.get("status", 200) != 200 and "body" not in ret:
            abort(ret.get("status", 200))
        else:
            resp = Response(
                status=ret.get("status", 200),
                response=ret.get("body", None),
                content_type=ret.get("content_type", None),
            )
            return resp

    app.debug = True
    app.run(host="0.0.0.0")
