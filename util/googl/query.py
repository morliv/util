from __future__ import annotations

import util.dictionary as d


class Query(str):
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
    def build(d: dict=None, pattern=None, skip={'id'}, logic_op='and') \
            -> Query: 
        expressions = []
        for k, v in d.items():
            if not (v is None or k in skip or pattern and k == 'name'):
                expressions.append(Query.expression(k, v))
        if pattern:
            expressions.append(Query.Clause.name_contains_pattern(pattern))
        return Query.concat(expressions, logic_op)

    @staticmethod
    def concat(expressions: list[str], logic_op='and') -> Query:
        return f' {logic_op} '.join(expressions)

    @staticmethod
    def expression(k, v):
        if isinstance(v, list):
            clauses = [Query.Clause.from_parts(k, e) for e in v]
            q = Query.concat(clauses, 'or')
            return Query(f"({q})") if len(clauses) > 1 else q
        return Query(Query.Clause.from_parts(k, v))
