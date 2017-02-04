from collections import OrderedDict
import json
import requests
import re

def _form_lists(tree, root):
    """'tree' will always be a dict, and 'root' is a key to a
    value in 'tree'.

    This is a recursive function that starts with a dict, and
    searches it for another dict that has only numbers as it's
    keys. This function will then convert that dict into a list
    and order the values by the numeric order of the keys.

    This function doesn't return anything. It modifies the dict
    passed to it by reference.
    """

    # If the value tree[root] is not a dict, this function does
    # nothing.
    if isinstance(tree[root], dict):

        # Checks if the first key of the dict at 'tree[root]'
        # is a number. If so, this function assumes the rest are
        # numbers also.
        if tree[root].keys()[0].isdigit():
            # Initializes the list that will be swapped out with
            # the dict.
            _list = []

            # Iterates the length of the dict. Assumes that the
            # number order starts with a 1.
            for i in range(1, len(tree[root]) + 1):
                # Extracts value.
                val = tree[root][str(i)]

                # If the value is a dict, calls this function on each
                # of it's keys, to create any lists from dicts they
                # may contain.
                if isinstance(val, dict):
                    for key in val.keys():
                        _form_lists(val, key)

                # Appends to value to new list.
                _list.append(val)

            # Reassigns list in place of dict with numeric keys.
            tree[root] = _list

        # This happens if first key of dict isn't a number.
        else:
            # Simply iterates through the keys, and calls this
            # function on each of it's key value pairs.
            for key in tree[root].keys():
                _form_lists(tree[root], key)

def convert(data, _tree=OrderedDict(), _first=1, delimiter="."):
    if _first:
        _tree = OrderedDict()

    # Iterates through key/value pairs of data.
    for key, val in data.iteritems():

        # The "." tells this function that the key needs to be broken
        # into, at least, two seperate keys.
        if delimiter in key:
            # Splits on '.' once. The left will be the key to a new
            # key value pair assigned to the left key.
            root, top = key.split(delimiter, 1)

                # If the 'root' doesn't already exist, initializes a dict
            # as it's value.
            if not _tree.has_key(root):
                _tree[root] = OrderedDict()

            # Passes the new key value pair, the dict that needs
            # updated, and a flag to indicate that this is a
            # recursive function call, to this function.
            convert({top: val}, _tree[root], 0)

        # This happens if the key/value pair are at an endpoint.
        else:
            # Simply updates the '_tree' dict with the key/value pair.
            #_tree.update({key: val})
            _tree[key] = val

    # This is only true on the initial call of this function.
    if _first:
        # Goes through completed dict and creates lists where the
        # keys of an internal dict are numeric.
        for key in _tree.keys():
            _form_lists(_tree, key)

        # Returns altered and completed _tree. Only returns on
        # original call, because the dict is altered/created
        # by reference internally.
        return _tree

