from typing import Optional, Callable
from functools import partial
import copy

def set(obj: type, response: Optional[dict], anew=False) -> type:
    if anew:
        obj = copy.deepcopy(obj)
    if response:
        for k, v in response:
            if hasattr(obj, k):
                setattr(obj, k, v)
    return obj

    
