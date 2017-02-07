"""
This is the “nester.py" module, and it provides one function called
print_lol() which prints lists that may or may not include nested lists
"""

def print_lol(the_list,indent=False,level=0):
    """
    This function takes two positional arguments; one called the_list"; which is any
    Python list (of, possibly, nested lists),
    and the other one is level which specifies number of tab_stops. Each data item in the provided list
    is (recursively) printed to the screen on its own line.
    """
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item,indent, level + 1)
        else:
            if indent:
                for tb_stop in range ( level ):
                    print("\t", end='')
            print(each_item)





