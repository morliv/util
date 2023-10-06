from typing import Optional, Callable

def update(obj, f: Callable):
    if not (response := call(f)):
        for k, v in response:
            if hasattr(obj, k):
                setattr(obj, k, v)

