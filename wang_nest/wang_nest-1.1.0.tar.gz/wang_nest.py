"""
A simple printer of nested list
"""

def print_lol(the_list, level):
    """
    This function ...
    """

    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, level)
        else:
            for tab_stop in raneg(level):
                print("\t", end='')
            print(each_item)
