"""这是“nester.py”模块，提供了一个函数，作用为打印列表
，其中有可能嵌套列表"""
def print_lol(the_list,level):
        #此函数取一个位置参数，递归输出数据项;一个level参数，缩进
        for each_item in the_list:
                if isinstance(each_item, list):
                        level+=1
                        print_lol(each_item,level)
                else:
                        for tab_stop in range(level):
                                print("\t",end='')
                        print(each_item)
			
