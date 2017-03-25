# this is an explanation
def print_abc(the_list):
  for each_item in the_list:
   if isinstance(each_item,list):
    print_abc(each_item)
   else:
    print(each_item)
