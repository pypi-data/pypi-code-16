"""This is the "recursiveFunctionForListsInAList.py" module, and it provides a function
called print_list() which prints lists that may or may not include nested lists."""

import sys
def print_list(the_list, indentation = False, level = 0, fh = sys.stdout):
    """This function takes a positional argument called 'the_list', which is any Python list (of, possibly, nested lists).
    Each data item in the provided list is (recursively) printed to the screen on its own line. A second argument called
    'indentation' is used to turn indentation of nested list on and off. However, the default value provided for this
    argument (False) turns off indentation features. So to turn it on, supply an argument value of True. A third
    argument called 'level' is used to insert tab-stops when a nested list is encountered. Lastly, an optional fourth
    argument 'fh' is used to save formatted data into a disk file."""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_list(each_item, indentation, (level + 1), fh)
        else:
            if indentation:
                for tab_stop in range(level):
                    print("\t", end='', file = fh)
            print(each_item, file = fh)
