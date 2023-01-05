from pathlib import Path

from sphinx.application import Sphinx
from sphinx.util.console import nocolor
from sphinxcontrib.websupport import WebSupport
from sphinxcontrib.websupport.storage.sqlalchemystorage import SQLAlchemyStorage

from .search import ESSearch

BASE_PATH = Path(__file__).resolve().parent.parent


def build(
    *,
    src: str,
    out: str,
    doctree: str,
    support: str,
    aws_host: str,
    aws_region: str,
    es_index_name: str,
):

    nocolor()

    websupport = WebSupport(
        srcdir=src,
        builddir=support,
        search=ESSearch(
            aws_host=aws_host,
            aws_region=aws_region,
            index_name=es_index_name,
        ),
        storage=SQLAlchemyStorage("sqlite://"),
    )
    websupport.build()

    sphinx = Sphinx(
        srcdir=src,
        confdir=src,
        outdir=out,
        doctreedir=doctree,
        buildername="html",
    )
    sphinx.config.html_context["essearch"] = True
    sphinx.build(force_all=True)
