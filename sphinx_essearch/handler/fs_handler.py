from pathlib import Path
from ..search import ESSearch
from .common import BaseHandler


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
