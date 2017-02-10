def print_lol(the_list,intend=0,level=0):
        for each_item in the_list:
                if isinstance(each_item,list):
                        print_lol(each_item,intend,level+1)
                else:
                        if intend==1:
                                for tab_stop in range(level):
                                        print "\t",
                                print(each_item)
                        else:
                                print(each_item)
