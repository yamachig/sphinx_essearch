from flask import (
    Flask,
    Response,
    abort,
    request,
)
from sphinx.util.console import nocolor

from .handle import Handler


def preview(
    *,
    out: str,
    support: str,
    aws_host: str,
    aws_region: str,
    es_index_name: str,
    search_html: str,
):
    app = Flask(__name__)
    handler = Handler(
        out=out,
        support=support,
        aws_host=aws_host,
        aws_region=aws_region,
        es_index_name=es_index_name,
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
