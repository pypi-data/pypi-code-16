def defaultify(value,default):
    if None == value:
        return default
    else:
        return value

def defaultifyDict(dictionary,key,default):
    if key in dictionary:
        return defaultify(dictionary[key],default)
    else:
        return default
