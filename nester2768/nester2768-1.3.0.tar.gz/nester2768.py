def nester(a,switch=False,level=0):
    for i in a:
        if isinstance(i,list):
            nester(i,switch,level+1)
        else:
            if switch:
                for m in range(level):
                    print ("\t",end='')
            print (i)
    print ('test nasb bar rooye local4')
    return

