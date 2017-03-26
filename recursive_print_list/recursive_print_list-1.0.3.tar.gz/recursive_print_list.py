#encoding:utf-8
"""此模块提供一个递归打印list内容函数"""
# you could use this model recursive print list item 
# 当使用python2.x 解决 print函数不换行.
from  __future__ import print_function
def printList(alist,indent= False,level = 0):
	if isinstance(alist,list):
		for each_item in alist:
			if isinstance(each_item,list):
				printList(each_item,indent,level+1)
			else:
				if indent:
				        for tab in range(level):
		 		              print("\t",end='')
  	 			print(each_item)


