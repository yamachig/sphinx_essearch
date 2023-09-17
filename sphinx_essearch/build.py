from pathlib import Path
import os

from sphinx.application import Sphinx
from sphinx.util.console import nocolor
from sphinxcontrib.websupport import WebSupport
from sphinxcontrib.websupport.storage.sqlalchemystorage import SQLAlchemyStorage
from sphinxcontrib.serializinghtml import SerializingHTMLBuilder

from .search import ESSearch

BASE_PATH = Path(__file__).resolve().parent.parent


def dump_context(self, context: dict, filename: str | os.PathLike[str]) -> None:
    context = context.copy()

    # if "css_files" in context:
    #     context["css_files"] = [css.filename for css in context["css_files"]]
    # if "script_files" in context:
    #     context["script_files"] = [js.filename for js in context["script_files"]]
    if self.implementation_dumps_unicode:
        with open(filename, "w", encoding="utf-8") as ft:
            self.implementation.dump(context, ft, *self.additional_dump_args)
    else:
        with open(filename, "wb") as fb:
            self.implementation.dump(context, fb, *self.additional_dump_args)


SerializingHTMLBuilder.dump_context = dump_context


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
