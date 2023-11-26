def one_to_one(iter1, iter2, condition):
    s1, s2 = set(iter1), set(iter2)
    for e1 in s1:
        match = None
        for e2 in s2:
            if condition(e1, e2):
                s2.discard(e2)
                match = True
        if not match:
            return False
    return True

            
