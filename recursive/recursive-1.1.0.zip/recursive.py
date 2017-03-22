movies=['start',1975,'terry',91,['haha',['mike','john','idle']]]
def view(func,level):
    for i in func:
                if isinstance(i,list):
                        view(i,level+1)
                else:
                        for tab_stop in range(level):
                                print ("\t\n")
                        print i
                
