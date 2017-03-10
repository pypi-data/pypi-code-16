'''这是一个打印列表数据项的模块'''
def pprintlist(thelist):

	for x in thelist:
		if isinstance(x,list):
			pprintlist(x)
		else:
			print(x)
