from dictionary import gets
from . import api, request, files, Query


class Response:
    def __init__(self, query: Query):
        self.q = query

    def list(self, pageToken: str=None) -> tuple[list, str]:
        fs, t = gets(self._page(pageToken), {'files': [], 'nextPageToken': []})
        return fs + (t and self.list(t))

    def _page(self, pageToken):
        FS = f"files({','.join(api.FIELDS | {'owners'})}),nextPageToken"
        return request(files.list(q=self.q, fields=FS, pageToken=pageToken))
