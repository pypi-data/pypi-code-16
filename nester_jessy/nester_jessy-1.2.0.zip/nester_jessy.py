"""这是一个print_lol.py模块，提供了print_lol函数，这个函数作用是打印列表，其中有可能包含（也有可能不包含）嵌套列表。"""
def print_lol(the_list, level = 0):
        """这个函数取一个位置参数，名为the_list，这可以是任何python列表（也可以是包含嵌套列表的列表），所指定的列表中的每个数据项递归的输出到屏幕上，各个数据占一行."""	
        for each_items in the_list:
                 if isinstance(each_items,list):
                        print_lol(each_items, level + 1)
                 else:
                        for tab_stop in range(level):
                                print("\t",end = '')
                        print(each_items)
