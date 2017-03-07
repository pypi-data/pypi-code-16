def nester(a,level=0):
    for i in a:
        if isinstance(i,list):
            nester(i,level+1)
        else:
            for m in range(level):
                print ("\t",end='')
            print (i)
    print ('test nasb bar rooye local4')
    return
