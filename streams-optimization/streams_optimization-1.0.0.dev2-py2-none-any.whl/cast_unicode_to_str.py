import json


def convert(input_data):
    """
    Converts all unicode entries in nested dict, list or string to python string.

    Parameters
    ----------
    input_data: dict, list or string

    Returns
    -------
    output:
        Same type as input with all unicode strings changed to python str format.
    """
    if isinstance(input_data, dict):
        return {convert(key): convert(value) for key, value in input_data.iteritems()}
    elif isinstance(input_data, list):
        return [convert(element) for element in input_data]
    elif isinstance(input_data, unicode):
        return str(input_data)
    else:
        return input_data


"""
The following code belongs to Mirec Miskuf answer (edited by Mark Amery) to StackOverflow thread:
http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python
"""

def json_load_byteified(file_handle):
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )
def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )
def _byteify(data, ignore_dicts = False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data

