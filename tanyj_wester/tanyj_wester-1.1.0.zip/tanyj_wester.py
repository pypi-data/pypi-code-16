"""提供一个print_lol函数，打印列表"""
def  print_lol(item_list,level=0):
	"""嵌套打印列表每个项各一行"""
	for each_item in item_list:
		if isinstance(each_item,list):
			print_lol(each_item,level+1)
		else:
                        for tab_stop in range(level):
                                print("\t",end="")
			print(each_item)
