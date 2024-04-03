from . import api, request, Query


class Response:
    def __init__(self, query: Query):
        self.q = query
