# -*- coding: cp936 -*-
"""
此函数可以迭代打印嵌套多层的列表中的数据项
"""
"""
这是“printapp”模块，提供了一个名为printapp()的函数，
这个函数的作用就是打印列表，其中有可能包含（也可能不包含）嵌套列表
"""
def printapp (the_list,level):
    for each_item in the_list:
        if isinstance(each_item,list):
            printapp(each_item,level+1)
        else:
            for tab_stop in range(level):
                print('\t')
            print(each_item)
            

