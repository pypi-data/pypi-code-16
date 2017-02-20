def check_types(obj, name, types, n=0):
    """check whether an object is a list
    Args:
        obj (object): an unknown object
        name (str): name of the object
        types (list): a hierarchy of types
    """
    if len(types) == 0:
        return (True, "")
    else:
        if not isinstance(obj, types[0]):
            msg = 'Error hint: field "{}"'.format(name)
            msg += " must be of type {}, ".format(str(types))
            msg += "but the received type is {}".format(type(obj))
            return (False, msg)
        else:
            # check each item has the required type
            if types[0] == list:
                next_level = "{}: level {}".format(name, n)

                def aux(obj):
                    return check_types(obj, next_level, types[1:], n+1)

                results = list(filter(lambda x: x[0], map(aux, obj)))
                if len(results) == 0:
                    return (True, "")
                else:
                    return results[0]
            else:
                return (True, "")
