def print_list(the_list,indent=False,level=0):
    for each_item in the_list:
        if isinstance(each_item,list):
            print_list(each_item,True,level+1)
        else:
            if indent==True:
                for x in range(level):
                    print('\t'),
            else:
                pass
            print(each_item)

movies = ['the holy grail',1975,'terry jones & terry gilliam',91,
['graham chapman',
['michael palin','johe cleese','terry giliiam','eric idle','terry jones']]]

print_list(movies,True,0)
