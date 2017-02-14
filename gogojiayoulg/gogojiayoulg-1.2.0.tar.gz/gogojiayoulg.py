'''HELLO this is a test
aaaaa
bbbbb
ccccc
'''

def print_lol(mylist,level):

    for x in mylist:
        if isinstance(x,list):
            print_lol(x,level+1)
        else:
            for y in range(level):
                print("\t",end="")
            print(x)
