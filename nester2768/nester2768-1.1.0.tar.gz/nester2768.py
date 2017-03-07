def nester(a,level):
    for i in a:
        if isinstance(i,list):
            nester(i,level+1)
        else:
            for m in range(level):
                print ("\t",end='')
            print (i)
    print ('test nasb bar rooye local3')
    return
