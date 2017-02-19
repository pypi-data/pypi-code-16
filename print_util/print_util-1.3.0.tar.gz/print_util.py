"""
print_loop just print list all element
"""
def print_loop(the_list, indent=False, level=0):
    for the_element in the_list:
        if isinstance(the_element, list):
            print_loop(the_element, indent, level+1)
        else:
            if indent :
                for i in range(level):
                    print("\t", end="")
            print(the_element)