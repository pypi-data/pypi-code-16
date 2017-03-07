def nester(a):
    for i in a:
        if isinstance(i,list):
            nester(i)
        else:
            print (i)
