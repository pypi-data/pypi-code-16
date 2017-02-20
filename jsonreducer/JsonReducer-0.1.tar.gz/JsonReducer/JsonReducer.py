"""
    This is a package based on the concept of Smaller Serialized Data, the implementation reduces the lenght of a JSON response as shown in the example.

    DEPENDENCIES:
        * collections
"""
import collections

def reducer(data):
    merged_array = {}

    if isinstance(data, list):
        for i in data:
            for k, v in i.iteritems():
                v = reducer(v)
                if k in merged_array:
                    merged_array[k].append(v)
                else:
                    merged_array[k] = [v]
    elif isinstance(data, dict):
        for k, v in data.iteritems():
            v = reducer(v)
            if k in merged_array:
                merged_array[k].append(v)
            else:
                merged_array[k] = [v]
    else:
        return data

    return merged_array
