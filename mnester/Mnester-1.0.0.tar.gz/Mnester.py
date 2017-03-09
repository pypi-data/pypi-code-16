"""movies = ["The Holy Grail", 1975, "Terry Jones & Terry Gilliam", 91,
           ["Graham Chapman", ["Michael Palin", "John Cleese", 
                                  "Terry Gilliam", "Eric Idel", "Terry Jones"]]]
"""

def print_movies(the_list):
	for each_item in the_list:
		if isinstance(each_item, list):
			print_movies(each_item)
		else:
			print(each_item)
			
#print_movies(movies)
