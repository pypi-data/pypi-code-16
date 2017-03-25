import sys
def print_easy(a_list, indent=True, level=0, fh=sys.stdout):
    """Prints each item in a list, recursively descending
       into nested lists (if necessary).Maybe print to file."""

    for each_item in a_list:
        if isinstance(each_item, list):
            print_easy(each_item, indent, level+1, fh)
        else:
            if indent:
               print("\t"*level, end='', file=fh)
            print(each_item, file=fh)

