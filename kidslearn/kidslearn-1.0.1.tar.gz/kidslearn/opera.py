'''for operation '''
import random


def getOpera(basenum):
    t = random.randint(0, 1)
    if t == 0:
        sub1 = random.randint(basenum, basenum + 8)
        subTemp = sub1 - basenum + 1
        sub2 = random.randint(subTemp, 9)
        return (sub1, sub2, "-", sub1 - sub2)
    else:
        add1 = random.randint(1, 9)
        subTemp = basenum - add1
        add2 = random.randint(subTemp, basenum - 1)
        return (add1, add2, "+", add1 + add2)