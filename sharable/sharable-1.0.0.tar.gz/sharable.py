def print_lol(the_list):
    for item in the_list:
        if isinstance(item, list):
            print_lol(item)
        else:
            print(item)

movies = [1,[2,3,4,[5,6,7]]]

print_lol(movies)
            
