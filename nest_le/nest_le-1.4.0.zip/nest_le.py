"""这是nest_le.py模块，提供了一个名为print_lol()的函数用来打印列表，其中包含或不包含嵌套列表。"""
import sys
def print_lol(the_list, indent=False, level=0, fn=sys.stdout):
        """这个函数有一个位置参数，名为"the_list"，这可以是任何python列表(包含或不包含嵌套列表)，所提供列表中的各个数据项会(递归地)打印到屏幕上，而且各占一行。
        第二个参数(名为"level")用来在遇到嵌套列表时插入制表符"""
        for each_item in the_list:
                if isinstance(each_item, list):
                        level = level + 1
                        print_lol(each_item, indent, level, fn)
                else:
                        if indent:
                                for tab_stop in range(level):
                                        print("\t", end='', file=fn)
                        print(each_item, file=fn)
		
movies = ['The Holy Grail', 1975, 'Terry Jones & Terry Gilliam', 91, ['Graham Chapman', ['Michael Palin', 'John Cleese', 'Terry Gilliam', 'Eric Idle', 'Terry Jones']]]

