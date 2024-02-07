from typing import Callable, Any

class Relation:
    def __init__(self, X, Y, f: Callable[[Any], bool]) -> None:
        self.X, self.Y = list(X), list(Y)
        self.f = f

    def one_to_one(self) -> bool:
        relation = [] 
        for x in self.X:
            match = False
            for y in self.Y:
                if self.f(x) == y:
                    match = True
                    self.Y.remove(y)
                    relation.append((x, y))
                    break
            if not match: return False
        return True

    def bijection(self) -> bool:
        return len(self.X) == len(self.Y) and self.one_to_one() 
