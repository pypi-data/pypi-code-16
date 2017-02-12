"""创建新函数
给函数命名"""
def print_lol(the_list,par1):
    """test1"""
    for lol in the_list:
        if isinstance(lol,list):
            print_lol(lol,par1+1)
        else:
            for tab_stop in range(par1):
                print("\t",end='')
            print(lol)
