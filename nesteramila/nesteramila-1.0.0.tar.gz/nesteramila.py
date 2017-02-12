"""
This is the “nester.py" module, and it provides one function called
print_items() which prints lists that may or may not include nested lists.
"""

def print_items(mList):
    """
    This function takes a positional argument called “the_list", which is any Python list (of, possibly, nested lists).
    Each data item in the provided list is (recursively) printed to the screen on its own line.

    :param mList:
    :return: nothing
    """
    for i in mList:
        if isinstance(i, list):
            print_items(i)
        else:
            print(i)