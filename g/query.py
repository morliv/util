from __future__ import annotations

from util import dictionary

class Query(str):
    class Clause(str):
        OPS = {'=': ['name', 'mimeType', 'fileId'], 'in': ['parents', 'owners']}
        VAL_FIRST_OPS = {'in'}

        @staticmethod
        def from_parts(key, val, op=None):
            op = dictionary.key_of_match_within_values(Query.Clause.OPS, key) or op
            return Query.Clause(f"'{val}' {op} {key}" if op in Query.Clause.VAL_FIRST_OPS else f"{key} {op} '{val}'")

        @staticmethod
        def name_contains_pattern(p: str) -> Query.clause:
            return Query.Clause(f'name contains {p}')

    @staticmethod
    def from_components(d: dict=None, pattern=None, logic_op='and'): 
        q = Query.concat([Query.expression(k, v) for k, v in d.items()])
        return Query.concat([q, Query.Clause.name_contains_pattern(pattern)]) if pattern else q

    @staticmethod
    def concat(expressions: List[str], logic_op='and') -> Query:
        return f' {logic_op} '.join(e for e in expressions)

    @staticmethod
    def expression(k, v):
        if isinstance(v, list):
            clauses = [Query.Clause.from_parts(k, e) for e in v]
            q = Query.concat(clauses, 'or')
            return Query(f"({q})") if len(clauses) > 1 else q
        return Query(Query.Clause.from_parts(k, v))

