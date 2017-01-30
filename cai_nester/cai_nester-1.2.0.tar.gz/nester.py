"""这是一个用来输出列表的函数，解决了列表中嵌套列表的问题"""
def print_lol(the_list,level=0):
  for a in the_list:
    if  isinstance(a,list):
      print_lol(a,level+1)
    else:
      for b in range(level):
        print("\t",end='')
      print(a)
