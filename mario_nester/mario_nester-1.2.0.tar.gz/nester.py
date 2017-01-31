"""This is the "nester.py" module"""
def print_lol(theList,level=0,indent=False):
        """This function takes one positional argument called "theList",which
            is any Python list.Each data item in the provided list is recursively
            printed to the screen on it's own line."""
        for item in theList:
                if isinstance(item,list):
                    print_lol(item,level+1,indent)
                else:
                    if indent:
                        for tab in range(level):
                                print("\t",end='')
                    print(item)
                    
