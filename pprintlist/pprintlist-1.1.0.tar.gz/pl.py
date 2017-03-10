'''这是一个打印列表数据项的模块'''
def pprintlist(thelist,level):
'''这是一个打印列表的函数'''
	for x in thelist:
		if isinstance(x,list):
			pprintlist(x,leve + 1)
		else:
			for fff in range(level):
				print('\t',end="")
			print(x)
