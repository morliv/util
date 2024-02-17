from __future__ import annotations
from typing import List
from googl import api, Service, File, Query

import dictionary as d

class Query(str):
    drive = api.service('drive', 3)

    class Clause(str):
        OPS = {'=': ['name', 'mimeType', 'fileId'], 'in': ['parents', 'owners']}
        VAL_FIRST_OPS = {'in'}

        @staticmethod
        def from_parts(key, val, op=None):
            op = op or d.key_of_match_within_values(Query.Clause.OPS, key)
            return Query.Clause(f"'{val}' {op} {key}" if op in Query.Clause.VAL_FIRST_OPS else f"{key} {op} '{val}'")

        @staticmethod
        def name_contains_pattern(p: str) -> Query.clause:
            return Query.Clause.from_parts('name', p, 'contains')

    @staticmethod
    def from_components(d: dict=None, pattern=None, logic_op='and'): 
        q = Query.concat([Query.expression(k, v) for k, v in d.items()], \
                         logic_op)
        return Query.concat([q, Query.Clause.name_contains_pattern(pattern)]) \
            if pattern else q

    @staticmethod
    def concat(expressions: List[str], logic_op='and') -> Query:
        return f' {logic_op} '.join(expressions)

    @staticmethod
    def expression(k, v):
        if isinstance(v, list):
            clauses = [Query.Clause.from_parts(k, e) for e in v]
            q = Query.concat(clauses, 'or')
            return Query(f"({q})") if len(clauses) > 1 else q
        return Query(Query.Clause.from_parts(k, v))

    def list(self) -> List[File]:
        results = []
        pageToken = None
        while pageToken != 'end':
            files, pageToken = self._list_page(pageToken)
            results += files
        return File.__files(results)

    def _list_page(self, pageToken: str='end'):
        LISTING = f"files({','.join(File.FIELDS | ['owners'])}),nextPageToken"
        response = api.request(Service.files.list(q=self, pageSize=1000,
            fields=LISTING, pageToken=pageToken))
        return response['files'], 