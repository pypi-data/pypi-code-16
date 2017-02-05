def print_lol(the_list, t=0):
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item, t+1)
		else:
			for time in range(t):
				print('\t', end='')
			print(each_item)
