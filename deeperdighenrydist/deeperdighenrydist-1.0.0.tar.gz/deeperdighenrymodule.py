"""this is the module "deeperdighenrymodule.py" 
	and it provides a function named print_lol, 
	which prints list , even the list included list in itself."""

def print_lol(the_list):
	#this function takes one positional argument called "the_list", which is any Python list.
	#each item in the list is printed to the screen on its own line.
         
	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item)
		else:
			print(each_item)
