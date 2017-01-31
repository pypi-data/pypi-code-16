# -*- coding: utf-8 -*-
"""This is the "nester.py" module and it provides one function called print_lol() 
   which prints lists that may or may not include nested lists."""

def print_lol(a_list, indent=False, depth=0):
    """This function takes one positional argument called "the_list", which 
        is any Python list (of - possibly - nested lists). Each data item in the 
        provided list is (recursively) printed to the screen on it’s own line."""

    for each_item in a_list:
        if isinstance(each_item, list):
            if indent == True:
                depth+=1
                print_lol(each_item, True, depth)
            else:
                print_lol(each_item)
        else:
            if indent == True:
                for i in range(depth):
                    print("\t", end='')
            print(each_item)

if __name__ == "__main__":
    movies =    ["The Holy Grail", 1975, "Terry Jones & Terry Gilliam", 91,
                ["Graham Chapman", ["Michael Palin", "John Cleese",
                 "Terry Gilliam", "Eric Idle", "Terry Jones"]]]
    print_lol(movies, True)
