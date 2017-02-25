"""这是“nester.py”模块，提供了一个函数，作用为打印列表
，其中有可能嵌套列表"""
def print_lol(the_list):
	#此函数取一个位置参数，递归输出数据项
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item)
		else:
			print(each_item)
			
