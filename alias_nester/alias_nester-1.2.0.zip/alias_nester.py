#!/usr/bin/env python
#_*_ coding:utf-8 _*_

"""这是"nester.py"模块，提供了一个名为print_lol()的函数，这个函数
的作用就是打印列表，其中有可能包含(也可能不包含)嵌套列表
"""
def print_lol(the_list,indent=False,level=0):
    """这哥函数取一个位置参数，名为the_list，这可以是任何python列表，
    也可以是包含嵌套列表的列表，所指定的列表中的每个数据项会递归的输出到
    屏幕上，各数据项各占一行
    indent参数表示输出时是否缩进，默认为False,不缩紧
    level参数用来控制遇到嵌套函数时，先打印制表符
    """
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,indent,level+1)    #调用函数本身
        else:
            if indent:
                for i in range(level):
                    print '\t',
            print each_item


m = [1,2,[3,[4,5,6]]]

