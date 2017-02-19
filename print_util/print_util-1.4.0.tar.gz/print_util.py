"""
print_loop just print list all element
"""
import sys
def print_loop(the_list, indent=False, level=0, device=sys.stdout):
    for the_element in the_list:
        if isinstance(the_element, list):
            print_loop(the_element, indent, level+1, device)
        else:
            if indent :
                for i in range(level):
                    print("\t", end="", file=device)
            print(the_element, file=device)