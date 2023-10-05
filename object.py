from typing import Optional, List

def update(obj, response: Optional[dict]):
    if not response:
        for k, v in response:
            if hasattr(obj, k):
                setattr(obj, k, v)
    return obj

def objs(obj, responses: List[Optional[dict]]):
    return [update(copy.deepcopy(obj), r) for r in responses if not None]

