import copy
from typing import Optional, Callable
from functools import partial

import dictionary as d


def set(obj: type, response, anew=False) -> Optional[type]:
    if anew:
        obj = copy.copy(obj)
    if isinstance(response, type(obj)):
        response = vars(response)
    if response:
        for k, v in response.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        return obj

def eq_attributes(first: type, second: type, ignore=[]):
    return dictionary(first, ignore) == dictionary(second, ignore)

def dictionary(obj: type, ignore=[]):
    return d.remove(vars(obj), ignore)
