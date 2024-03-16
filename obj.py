import copy


def set(obj: type, response, anew=False) -> type | None:
    if anew:
        obj = copy.deepcopy(obj)
    if isinstance(response, type(obj)):
        response = vars(response)
    if response:
        for k, v in response.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        return obj

def update(o: type, o2: type):
    for a in vars(o).keys():
        if hasattr(o2, a):
            setattr(o, a, getattr(o2, a))
    return o


def eq_attributes(first: type, second: type, ignore=[]):
    return dictionary(first, ignore) == dictionary(second, ignore)

def dictionary(obj: type, ignore=[]):
    return d.remove(vars(obj), ignore)
