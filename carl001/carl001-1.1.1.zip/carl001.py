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

def print_lol(the_list,level):
    '''
    这个函数通过判断'''
    for each_item in the_list :
        if isinstance(each_item,list):
            print_lol(each_item,level+1)
        else :
            for tab_stop in range(level)
                print('\t',end='')
            print(each_item)