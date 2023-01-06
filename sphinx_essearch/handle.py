import mimetypes
from pathlib import Path
from .templates import get_dir
from typing import TypedDict, Union
from .search import ESSearch
from abc import ABCMeta, abstractmethod
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
    content_type: Union[str, None]


class BaseHandler(metaclass=ABCMeta):
    def __init__(
        self,
        *,
        search: ESSearch,
        search_html: str,
    ):
        self.search = search
        self.search_html = search_html

    @abstractmethod
    def get_file_bytes(self, path_str: str) -> Union[bytes, None]:
        raise NotImplementedError

    def handle(
        self,
        *,
        path_str: str,
        args: dict[str, str],
    ) -> Response:

        b = self.get_file_bytes(path_str)
        if b is None:
            return {
                "status": 404,
            }

        if path_str == f"/{self.search_html.lstrip('/')}":
            q = args.get("q")
            matches = self.search.handle_query(q)
            search_body_template = j2_env.get_template("search_body.html")
            search_body = search_body_template.render(
                matches=matches,
            )

            html = b.decode("utf-8").replace(
                "<!-- body_place -->",
                search_body,
            )
            return {
                "status": 200,
                "body": html,
            }

        else:
            return {
                "status": 200,
                "body": b,
                "content_type": get_content_type(Path(path_str).name),
            }


class FSHandler(BaseHandler):
    def __init__(
        self,
        *,
        search: ESSearch,
        search_html: str,
        out: str,
    ):
        super().__init__(
            search=search,
            search_html=search_html,
        )
        self.out_dir = out

    def get_file_bytes(self, path_str: str):
        out_dir_path = Path(self.out_dir)
        path = (out_dir_path / path_str.lstrip("/")).resolve()
        if path.exists():
            return path.read_bytes()
        else:
            return None
