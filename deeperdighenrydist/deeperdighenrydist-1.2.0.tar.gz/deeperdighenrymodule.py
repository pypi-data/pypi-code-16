"""this is the module "deeperdighenry.py" 
	and it provides a function named print_lol, 
	which prints list , even the list included list in itself."""

def print_lol(the_list,level=0):
	#this function takes one positional argument called "the_list", which is any Python list.
	#each item in the list is printed to the screen on its own line.
    #level is a marker for indent.
	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item,level+1)
		else:
			for num in range(level):
				print("\t",end='')
			print(each_item)
