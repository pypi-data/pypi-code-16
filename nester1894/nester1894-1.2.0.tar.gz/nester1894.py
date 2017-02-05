def print_lol(the_list, indent=False, t=0):
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item, indent, t+1)
		else:
			if indent :
				print('\t' * t, end='')
			print(each_item)