def print_list(the_list,level=0):
    for each_item in the_list:
        if isinstance(each_item,list):
            print_list(each_item,level+1)
        else:
            for x in range(level):
                print('\t'),
            print(each_item)

movies = ['the holy grail',1975,'terry jones & terry gilliam',91,
['graham chapman',
['michael palin','johe cleese','terry giliiam','eric idle','terry jones']]]

print_list(movies,0)
