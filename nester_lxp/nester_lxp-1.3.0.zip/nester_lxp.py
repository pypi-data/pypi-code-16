#这是4.py模块，提供一个名为print_lol()的函数
def print_lol(the_list,indent=False,level=0):    
    """这个函数去一个位置参数，名为"the_lisr"，这可以是任何python列表
    （也可以是包含嵌套列表的列表）。所指定的列表中的每个数据项会
    （递归地）输出到屏幕上，各数据项各占一行"""
    for each_item in the_list:
        if isinstance(each_item,indent,list):
            print_lol(each_item,level+1)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t",end='')
            print(each_item)
