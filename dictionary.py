def replace_key(dictionary: dict, previous: str, new: str) -> dict:
    if previous in dictionary:
        dictionary[new] = dictionary[previous]
        del dictionary[previous]
    return dictionary

def key_of_match_within_values(d, val):
    for k, list_vals in d.items():
        if val in list_vals:
            return k
    return None

def recursive_map(value, func):
    if isinstance(value, dict):
        return {k: recursive_map(v, func) for k, v in value.items()}
    else:
        return func(value)
        
