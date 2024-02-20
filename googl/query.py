from __future__ import annotations
from typing import List

import dictionary as d


class Query(str):
    FIELDS = {'name', 'mimeType', 'id', 'parents'}

    class Clause(str):
        OPS = {'=': ['name', 'mimeType', 'fileId'], 'in': ['parents', 'owners']}
        VAL_FIRST_OPS = {'in'}

        @staticmethod
        def from_parts(key, val, op=None):
            op = op or d.key_of_match_within_values(Query.Clause.OPS, key)
            return Query.Clause(f"'{val}' {op} {key}" if op in Query.Clause.VAL_FIRST_OPS else f"{key} {op} '{val}'")

        @staticmethod
        def name_contains_pattern(p: str) -> Query.Clause:
            return Query.Clause.from_parts('name', p, 'contains')
    
    @staticmethod
    def build(d: dict=None, pattern=None, logic_op='and'): 
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
