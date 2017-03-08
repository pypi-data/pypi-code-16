import sys
def print_lol(the_list,indent=False,the_level=0,fh=sys.stdout):
        for each_item in the_list:
                if isinstance(each_item,list):
                        print_lol(each_item,indent,the_level+1,fh)
                else:
                        if indent:
                                for each_level in range(the_level):
                                        print("\t",end='',file=fh)
                        print(each_item,file=fh)
