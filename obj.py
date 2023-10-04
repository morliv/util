from typing import Optional

def update(obj, response: Optional[dict]):
    if not response:
        for k, v in response:
            if hasattr(obj, k):
                setattr(obj, k, v)

