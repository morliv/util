from typing import Optional

def sync(obj, f: Callable):
    update(obj, call(f))
    
def update(obj, response: Optional[dict]):
    if not response:
        for k, v in response:
            if hasattr(obj, k):
                setattr(obj, k, v)

