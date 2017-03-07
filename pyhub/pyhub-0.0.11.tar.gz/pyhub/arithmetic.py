import sys

def config():
    reload(sys)
    sys.setdefaultencoding('utf-8')
    print 'pyhub lib is running! and encoding is %s'% str(sys.getdefaultencoding())

#from top to bottom,left to right
#lst like this [(2,3),(5,6)]
def tip_paixuzb_maopao():
    print "lst like this style [(2,3),(3,6)]"
    print "output from top to bottom,left to right"

def paixuzb_maopaoy2x(lst):

    b = []
    l = len(lst)
    for i in range(l):
        j = i
        for j in range(l):
            if (lst[i][0] < lst[j][0]):
                lst[i], lst[j] = lst[j], lst[i]
            if (lst[i][1] > lst[j][1]):
                lst[i], lst[j] = lst[j], lst[i]

    for k in range(len(lst)):
        b.append(lst[k])
    return b

def paixuzb_maopaox2y(lst):
    b = []
    l = len(lst)
    for i in range(l):
        j = i
        for j in range(l):
            if (lst[i][1] < lst[j][1]):
                lst[i], lst[j] = lst[j], lst[i]
            if (lst[i][0] < lst[j][0]):
                lst[i], lst[j] = lst[j], lst[i]

    for k in range(len(lst)):
        b.append(lst[k])
    return b