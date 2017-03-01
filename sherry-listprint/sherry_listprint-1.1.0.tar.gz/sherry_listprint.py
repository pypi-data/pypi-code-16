"""打印列表函数，并检验是否有内嵌列表"""
def print_lol(the_list,level):
        """the_list:位置参数，递归打印列表中的每一项到每一行;
             level:缩进控制参数，控制每行缩进程度"""
        for each_item in the_list:
                if isinstance(each_item,list):
                        print_lol(each_item,level+1)
                else:
                        for tab_stop in range(level):
                                print("\t",end='')
                        print(each_item)

