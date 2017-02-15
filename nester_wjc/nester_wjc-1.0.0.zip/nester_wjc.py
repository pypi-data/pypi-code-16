# -*- coding: UTF-8 -*-
"""
这是nester.py 模块，提供一个名为printValue()的函数，
这个函数的作用是打印列表，其中有可能包含（也有可能不包含）嵌套列表
"""
def printValue(nlist) :
    """
    这个函数包含一个位置参数，名为nlist，这可以是任何python列表（可以是包含嵌套列表的列表）。
    列表中的每个数据项会（递归地）输出到屏幕上，各数据项各站一行
    :param nlist:   python列表
    :return: 列表中的数据项
    """
    for each_item in nlist :
        if isinstance(each_item,list) :
            printValue(each_item)
        else :
            print(each_item)


if __name__ == "__main__":
    test_movies = ["The Holy Grail",1975,"Terry Jones",91,["Graham Chapman",["Michael","John Cleese","Terry Gilliam","Eric Idle"]]]
    printValue(test_movies)