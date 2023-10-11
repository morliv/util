from typing import Optional, Callable
from functools import partial
import copy

def set(obj: type, response, anew=False) -> type:
    if anew:
        obj = copy.copy(obj)
    if isinstance(response, type(obj)):
        response = vars(response)
    if response:
        for k, v in response.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
    return obj

    
