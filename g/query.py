from util import dictionary

class Query(str):
    class Clause(str):
        OPS = {'=': ['name', 'mimeType', 'fileId'], 'in': ['parents', 'owners']}
        VAL_FIRST_OPS = {'in'}

        @staticmethod
        def from_parts(key, val, op=None):
            op = dictionary.key_of_match_within_values(Query.Clause.OPS, key) or op
            return Query.Clause(f"'{val}' {op} {key}" if op in Query.Clause.VAL_FIRST_OPS else f"{key} {op} '{val}'")

    @classmethod
    def __new__(cls, value):
        return str.__new__(cls, Query.add_ownership(value))

    @staticmethod
    def from_components(d: dict={}, pat=None, logic_op='and'): 
        return Query.concat([Query.expression(k, v) for k, v in d.items()]).add_contains_pattern(pat)

    def add_contains_pattern(self, pat: str=None):
        return Query.concat([self, Query.Clause(f'name contains {pat}')]) if pat else self

    @staticmethod
    def add_ownership(q: str) -> Query:
        return Query.concat([q, Query.Clause.from_parts('owners', 'me')])
        
    @staticmethod
    def concat(expressions: List[Query], logic_op='and'):
        return f' {logic_op} '.join(list(filter(lambda e: e, expressions)))

    @staticmethod
    def expression(k, v):
        if isinstance(v, list):
            clauses = [Query.Clause.from_parts(k, e) for e in v]
            q = Query.concat(clauses, 'or')
            return Query(f"({q})") if len(clauses) > 1 else q
        return Query(Query.Clause.from_parts(k, v))

