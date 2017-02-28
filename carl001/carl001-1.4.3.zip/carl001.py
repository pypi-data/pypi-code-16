#coding=utf-8

'''
这个模块用于
将一个多层嵌套的列表中的每一项
在屏幕上显示出来
'''
'''
这是“nester.py”模块，提供了一个名为print_lol()的函数，这个函数的作用是打印列表，
其中有可能包含（也有可能不包含）嵌套列表。
'''

'''2017年2月28日14:52:59
def print_lol(the_list,indent=False,level=0):
    for each_item in the_list :
        if isinstance(each_item,list):
            print_lol(each_item,indent,level+1)
        else :
            if indent :
                for tab_stop in range(level):
                    print('\t',end='')
            print(each_item)

'''

import sys

def print_lol(the_list,indent=False,level=0,fh = sys.stdout):    #2017年2月28日14:59:40
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,indent,level+1,fh)
        else:
            if indent:
                for tab_stop in rage(level):
                    print('\t',end='',file = fh)
            print(each_item,file = fh)

