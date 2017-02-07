def reduce(merge, collection, base):
    """reduce

    Args:
        merge (function): a function that merges two objects
        collection (list): a list of objects
        base (object): a base case object
    Returns:
        a reduced object
    """
    def tail(xs): return xs[1:]

    if len(collection) == 0:
        return base
    else:
        return reduce(merge, tail(collection), merge(base, collection[0]))
