# -*- coding: UTF-8 -*-
"""
这是nester_wjc.py 模块，提供一个名为printValue()的函数，
这个函数的作用是打印列表，其中有可能包含（也有可能不包含）嵌套列表
"""
def printValue(nlist,indent = False,level = 0) :
    """
    这个函数包含一个位置参数，名为nlist，这可以是任何python列表（可以是包含嵌套列表的列表）。
    列表中的每个数据项会（递归地）输出到屏幕上，各数据项各站一行
    :param nlist:   python列表
    :param indent:  可选参数，表示是否开启嵌套列表缩进显示功能，默认不开启
    :param level:   可选参数，表示开始缩进位（制表符），如果是负值，表示不用缩进
    :return: 列表中的数据项
    """
    if level < 0 :
        level = -20
        # 这样做的目的是确保负值不会被缩进
    for each_item in nlist :
        if isinstance(each_item,list) :
            printValue(each_item,indent,level + 1)
        else :
            if indent :
                for num in range(level):
                    print('\t',end="")
                # 可以替换为 print('\t'*level,end='')
            print(each_item)


if __name__ == "__main__":
    test_movies = ["The Holy Grail",1975,"Terry Jones",91,["Graham Chapman",["Michael","John Cleese","Terry Gilliam","Eric Idle"]]]
    printValue(test_movies,True)