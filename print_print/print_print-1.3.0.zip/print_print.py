def print_tab(the_list,indent=False,lever=0):
        for each_item in the_list:
                if isinstance(each_item,list):
                        print_tab(each_item,indent,lever+1)
                else:
                        if indent:
                                for each_tap in range(lever):
                                        print("\t",end="")
                        print(each_item)
                                        
                                        
                                
                                        
                                
                                
