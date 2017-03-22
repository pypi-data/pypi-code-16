

def funxuner(die_list,indent=False,level=0):


    for erzi in die_list:  
        if isinstance(erzi,list):   
            funxuner(erzi,indent,level+1)  
        else:
            if indent:
                print('\t'*level,end='')   
            print(erzi)    

