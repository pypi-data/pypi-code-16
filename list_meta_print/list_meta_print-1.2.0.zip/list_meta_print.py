def list_print(theList, indent = False, level = 0):
	for l in theList:
		if isinstance(l, list):
                        list_print(l, indent, level + 1)
		else:
                    if indent:
                        for i in range(level):
                            print("\t", end='')
                    print(l)
