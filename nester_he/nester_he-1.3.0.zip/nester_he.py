"""创建新函数
给函数命名"""
def print_lol(the_list,indent=False,par1=0):
    """test1"""
    for lol in the_list:
        if isinstance(lol,list):
            print_lol(lol,indent,par1+1)
        else:
            if indent==True:
                for tab_stop in range(par1):
                    print("\t",end='')
            print(lol)
