"""This is the "nester.py" module and it provides one function print_lol() whcih
   prints lists that may or may not include nested lists."""
def print_lol(the_list):
    """this function takes one positional arfument called "the list", which is
       any Python list (of = possibly - nested lists). Each data item in the
       provided list is (recursively) printed to the screen on its own line."""
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item)
        else:
            print(each_item)
