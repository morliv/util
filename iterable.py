class Comparative:
    def __init__(self, domain, codomain, condition) -> None:
        self.domain, self.codomain = list(domain), list(codomain)
        self.condition = condition

    def one_to_one(self):
        for e1 in self.domain:
            match = None
            for e2 in self.codomain:
                if self.condition(e1, e2):
                    self.codomain.remove(e2)
                    match = True
            if not match:
                return False
        return True

    def bijection(self):
        return len(self.domain) == len(self.codomain) and self.one_to_one()
