def replace_key(dictionary: dict, previous: str, new: str) -> dict:
    if previous in dictionary:
        dictionary[new] = dictionary[previous]
        del dictionary[previous]
    return dictionary
