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

    search = None
    if aws_host and aws_region and es_index_name:
        search = ESSearch(
            aws_host=aws_host,
            aws_region=aws_region,
            index_name=es_index_name,
        )
    else:
        print(
            "[sphinx_essearch][warn] aws_host, aws_region or es_index_name not specified"
        )

    websupport = WebSupport(
        srcdir=src,
        builddir=support,
        search=search,
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
    sphinx.config.html_context["essearch"] = search is not None
    sphinx.build(force_all=True)
