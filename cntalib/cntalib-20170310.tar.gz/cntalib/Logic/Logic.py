# -*- coding: utf-8 -*-
#Logic_function 逻辑类函数
import numpy as np


#CROSSUP 交叉    返回最近N周期内金叉与死叉次数 返回值为int N不小于2 第一个数是金叉，第二个数是死叉
#参数的顺序为 A交叉B， 比如A向上金叉B，则返回1
#参数 A ,B 是两个list,长度一样; N是周期 N不大于A的长度，且不小于2
def CROSS(A,B,N):
    if N<2:
        return float('NaN')
    else:
        A=A[-N:]
        B=B[-N:]
    dif=np.array(A)-np.array(B)
    dif=dif/abs(dif)
    stk_dif=np.diff(dif)
    return (list(stk_dif).count(2) ,list(stk_dif).count(-2))



#维持一段周期后交叉,就是说N周期内金交叉只有一次 返回值为int   第一个数是金叉   第二个是死叉
#N的选择依据以list以最后的数为基准
def LONGCROSS(A,B,N):
    e1,e2=CROSS(A,B,N)
    if(e1<=1) and (e2<=1):
        return (e1,e2)

#返回A数组list是否在N周期内是连续大于 返回值为int,1为真，0为假
#N以最后的数为基准
def NDAY(A,N):
    if N>len(A):
        return float('NaN')
    dif=np.diff(A[-N:])
    dif=dif/abs(dif)
    if sum(dif)==len(A)-1:
        return 1
    else:
        return 0

#返回A数组list是否在N周期内是连续小于 返回值为int,1为真，0为假
#N以最后的数为基准
def UPNDAY(A,N):
    if N>len(A):
        return float('NaN')
    dif=np.diff(A[-N:])
    dif=dif/abs(dif)
    print(sum(dif))
    if sum(dif)==1-len(A):
        return 1
    else:
        return 0
        









