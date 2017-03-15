def print_lol(the_list):
    # print a list 
    # a test from a primary python user
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item)
        else:
            print(each_item)
