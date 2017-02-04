def solve(L):
	for each_item in L:
		if isinstance(each_item, list):
			solve(each_item)
		else:
			print(each_item)
			
