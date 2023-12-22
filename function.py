import inspect
from typing import Callable

def keys(func: Callable):
    params = inspect.signature(func).parameters
    return list(params.keys())

