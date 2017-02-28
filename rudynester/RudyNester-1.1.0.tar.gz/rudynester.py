"""This is the "nester.py" module and it provides one function caled print_lol()
which prints lists that may or may not include nested lists."""
def print_lol(the_list, level):
    """This function takes a positional argument called "the list", Which
    is any Python list (of-ossibly-nested lisists).  Each data item in the
    provided list is (recurseively printed to the sreen on it's own line.
    A second argument called "level" is used to insert tab-stops when a nested list encountered"""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, level+1)
        else:
            for tab_stop in range(level):
                print("\t",end='')
            print (each_item)
                      

                      
