movies=['start',1975,'terry',91,['haha',['mike','john','idle']]]
def view(func,level=0,indent=False):
    for i in func:
                if isinstance(i,list):
                        view(i,level+1,indent)
                else:
                        if indent:
                                for tab_stop in range(level):
                                        print ("\t\n")
                        print i
                
