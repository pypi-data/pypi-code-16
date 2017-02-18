movies = ["the holy grail",1975, "the life of brain", 91,
["the meaning of life",["Graham Chapman","Micheal Palin", "John Cleese"]]]
def print_lol(the_list, level):
  for movie in the_list:
    if isinstance(movie,list):
        level = level+1
        print_lol(movie, level)
    else:
        for num in range(level):
          print("\t",end='')
        print(movie,level)
print_lol(movies,0)