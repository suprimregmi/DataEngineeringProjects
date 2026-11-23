def contains_duplicate(array):
    store = {}
    for i, j in enumerate(array):
        if j in store:
            return True
        store[j] = i
    return False
