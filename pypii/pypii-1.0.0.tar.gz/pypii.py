def print_lol(the_list):
    for iterator in  the_list:
        if  isinstance(iterator, list):
            print_lol(iterator)

        else:
            print iterator

cast=['bill','sam','joe','root',['sim',['baa',['foo']]]]
print_lol(cast)
