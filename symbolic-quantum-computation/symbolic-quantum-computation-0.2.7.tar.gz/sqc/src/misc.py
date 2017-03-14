def get_index(lst, obj):
    for i in range(len(lst)):
        if id(lst[i]) == id(obj):
            return i

    raise Exception('No such element in list')
