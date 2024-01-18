def nestedly(listed, f: callable):
    if isinstance(listed, list):
        return [nestedly(e, f) for e in listed]
    return f(listed)
