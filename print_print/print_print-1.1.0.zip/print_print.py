def print_tab(the_list,lever):
	for each_item in the_list:
		if isinstance(each_item,list):
			print_tab(each_item,lever+1)
		else:
			for each_tap in range(lever):
				print("\t",end="")
			print(each_item)			
