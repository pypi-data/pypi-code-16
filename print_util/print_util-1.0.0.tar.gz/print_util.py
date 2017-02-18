"""
print_loop just print list all element
"""
def print_loop(the_list):
    for the_element in the_list:
        if isinstance(the_element, list):
            print_loop(the_element)
        else:
            print(the_element)