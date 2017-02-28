"""打印列表函数，并检验是否有内嵌列表"""
def print_lol(the_list):
        """the_list:位置参数；递归打印列表中的每一项到每一行"""
        for each_item in the_list:
                if isinstance(each_item,list):
                        print_lol(each_item)
                else:
                        print(each_item)

