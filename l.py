from typing import Callable, TypeVar

def nestedly(listed, f: Callable):
    if isinstance(listed, list):
        return [nestedly(e, f) for e in listed]
    return f(listed)

T = TypeVar('T')

def one(l: list[T], create: Callable[[], T], delete: Callable[[T], None]) \
        -> T:
    for i, e in reversed(list(enumerate(l))):
        if i == 0: return e
        delete(e)
    return create()
