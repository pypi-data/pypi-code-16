"""创建新函数
给函数命名"""
def print_lol(the_list):
    """test1"""
    for lol in the_list:
       if isinstance(lol,list):
          print_lol(lol)
       else:
           print(lol)
