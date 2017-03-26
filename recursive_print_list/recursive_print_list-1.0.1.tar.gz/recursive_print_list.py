#encoding:utf-8
"""此模块提供一个递归打印list内容函数"""
# you could use this model recursive print list item 

def printList(Alist,level):
	if isinstance(Alist,list):
		for each_item in Alist:
			if isinstance(each_item,list):
				printList(each_item,level+1)
			else:
			        for tab in range(level):
	 		                print("\t")
  	 			print(each_item)


