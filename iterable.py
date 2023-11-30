from typing import Callable

class Comparative:
    def __init__(self, domain, range, f: Callable) -> None:
        self.domain, self.range = list(domain), list(range)
        self.f = f

    def one_to_one(self):
        relation = [] 
        for e1 in self.domain:
            match = None
            for e2 in self.range:
                if self.f(e1) == e2:
                    match = True
                    self.range.remove(e2)
                    relation.append((e1, e2))
                    break
            if not match:
                return None
        return relation

    def bijection(self):
        return self.one_to_one() if len(self.domain) == len(self.range) else None
