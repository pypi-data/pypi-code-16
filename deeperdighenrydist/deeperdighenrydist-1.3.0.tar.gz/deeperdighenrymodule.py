"""this is the module "deeperdighenry.py" 
	and it provides a function named print_lol, 
	which prints list , even the list included list in itself."""

def print_lol(the_list,indent = False,level=0):
	#this function takes one positional argument called "the_list", which is any Python list.
	#each item in the list is printed to the screen on its own line.
    #level is a marker for indent.
    #indent is a switch telling the intepreter indent or not.
	for each_item in the_list:
		if isinstance(each_item,list):
			print_lol(each_item,indent,level+1)
		else:
			if indent:
				for num in range(level):
					print("\t",end='')
			print(each_item)
