"""递归循环"""
def print_lol_sjl(the_list):
	for item in the_list:
		if isinstance(item, list):
			print_lol(item)
		else:
			print(item)







