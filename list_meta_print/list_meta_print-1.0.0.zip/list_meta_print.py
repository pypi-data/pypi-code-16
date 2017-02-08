def list_print(theList):
	for l in theList:
		if isinstance(l, list):
			list_print(l)
		else:
			print(l)
