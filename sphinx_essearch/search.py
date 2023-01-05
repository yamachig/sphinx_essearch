import re

from opensearchpy import (
    OpenSearch,
    RequestsHttpConnection,
    AWSV4SignerAuth,
    NotFoundError,
)
import boto3
from sphinxcontrib.websupport.search import BaseSearch


class ESSearch(BaseSearch):
    def __init__(self, *, aws_host: str, aws_region: str, index_name: str):
        super().__init__(None)
        self.index_name = index_name

        credentials = boto3.Session().get_credentials()
        auth = AWSV4SignerAuth(credentials, aws_region)

        self.es = OpenSearch(
            hosts=[{"host": aws_host, "port": 443}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
        )

    def init_indexing(self, changed=[]):
        super().init_indexing(changed)
        try:
            self.es.delete_by_query(
                index=self.index_name,
                body={"query": {"match_all": {}}},
            )
        except NotFoundError:
            pass

        if not self.es.indices.exists(index=self.index_name):
            self.es.indices.create(index=self.index_name)

    def add_document(self, pagename, srcname, title, text):
        path = pagename + ".html"

        self.es.index(
            index=self.index_name,
            id=path,
            body={
                "path": f"{path}",
                "srcname": srcname,
                "title": re.sub(r"<.*?>", "", title),
                "text": text,
            },
        )

    def handle_query(self, q):
        keywords = q.split()
        re_keywords = re.compile("|".join(keywords), re.I)
        matches = self.es.search(
            index=self.index_name,
            body={
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    "text": keyword,
                                },
                            }
                            for keyword in keywords
                        ],
                    },
                },
            },
        )
        hits = matches["hits"]["hits"]
        for hit in hits:
            doc = hit["_source"]
            all_text = doc["text"]
            html = ""
            last_end = 0
            last_text_end = -20
            while len(html) < 200:
                m = re_keywords.search(
                    all_text,
                    pos=last_end,
                )
                if not m:
                    break
                start = m.start()
                end = m.end()
                if html and last_text_end < start - 20:
                    html += "…"
                text = all_text[max(last_text_end, start - 20) : end + 20]
                html += re_keywords.sub(
                    r"<em>\g<0></em>",
                    text,
                )
                last_end = end
                last_text_end = end + 20

            yield doc["path"], doc["title"], html
