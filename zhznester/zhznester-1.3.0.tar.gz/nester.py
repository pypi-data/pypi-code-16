'''这是一个print_lol函数，主要的作用是用来打印列表里的所有项目，如果列表里嵌套了好多列表也可以解决哦'''
def print_lol(the_list, indent=False, level=0):
	'''我们这个函数可以打印任何python列表，每个数据项各占一行，遇到嵌套列表会自动打印tab'''
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item, indent, level+1)
		else:
			if indent:
				for tab_stop in range(level):
					print('\t')
			print(each_item)
