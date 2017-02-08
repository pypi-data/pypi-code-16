def list_print(theList, level):
	for l in theList:
		if isinstance(l, list):
                        list_print(l, level + 1)
		else:
                    for i in range(level):
                        print("\t", end='')
                    print(l)
