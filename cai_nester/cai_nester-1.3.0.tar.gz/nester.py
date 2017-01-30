"""这是一个用来输出列表的函数，解决了列表中嵌套列表的问题"""
def print_lol(the_list,indent=False,level=0):
  for a in the_list:
    if  isinstance(a,list):
      print_lol(a,indent,level+1)
    else:
      if indent:
        for b in range(level):
          print("\t",end='')
      print(a)
