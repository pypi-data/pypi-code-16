
# -*- coding: utf-8 -*-
#Reference_function 引用类函数
import pandas as pd
import numpy as np

def MIDPOINT(df, n, price='Close'):
    """
    MidPoint over period
    source: http://www.tadoc.org/indicator/MIDPOINT.htm
    """
    midpoint_list = []
    i = 0
    while i < len(df[price]):
        if i + 1 < n:
            midpoint = float('NaN')
        else:
            start = i + 1 - n
            end = i + 1
            midpoint = (max(df[price][start:end]) + min(df[price][start:end])) / 2
        midpoint_list.append(midpoint)
        i += 1
    return midpoint_list



#DateFrame求简单移动平均线 返回一个DataFrame
def df_MA(DataFrame,ma_lst=[5,10],price='close'):
    for ma in ma_lst:
        DataFrame['MA_' + str(ma)] = DataFrame[price].rolling(window=ma,center=False).mean()
    return DataFrame
#指数平滑移动平均线EMA
def df_EMA(DataFrame,span_lst=[5,10],price='close'):
    
    for span in span_lst:
        DataFrame['EMA_' + str(span)] = DataFrame[price].ewm(span).mean()
    return DataFrame
#指数平滑移动平均Y=〔2*X+(N-1)*Y’〕/(N+1)，  EXPMA
def EMA(X,N):
    emals=[]
    for i in range(0,len(X)):
        if i==0:
            emals.append(X[i])
        else:
            Y=(2*X[i]+(N-1)*emals[i-1])/(N+1)
            emals.append(Y)
    return(emals)

#返回积累平均 SMA(X,N,M):X的N日移动平均,M为权重,如Y=(X*M+Y'*(N-M))/N
def SMA(X,N,M):
    if not(N>M):
        return float(float('NaN'))
    smalst=[]
    for i in range(0,len(X)):
        if i==0:
            smalst.append(X[i])
        else:
            Y=(M*X[i]+smalst[i-1]*(N-M))/N
            smalst.append(Y)
    return(smalst)
#平滑移动平均 等于 SMA(X,N,1)
def MEMA(X,N):
    return(SMA(X,N,1))

#动态移动平均若Y=DMA(X，A)则 Y=A*X+(1-A)*Y'，其中Y'表示上一周期Y值，A必须小于1。
def DMA(X,A):
    lst=[]
    if not(A>0 and A<1):
        return float('NaN')
    
    for i in range(0,len(X)):
        if i==0:
            lst.append(X[i])
        else:
            Y=A*X[i]+(1-A)*lst[i-1]
            lst.append(Y)
    return(lst)    

#SUMBARS_single 累加到指定值的周期数 返回单个int
def SUMBARS_single(X,A):
    ln_x=len(X)-1
    i=ln_x-1
    out=0
    while(i>=0):
        s=sum(X[(i):])
        if s >=A :
            out=len(X)-i
            break
        i=i-1
    return out
##SUMBARS 累加到指定值的周期数 返回list
def SUMBARS(X,A): 
    ls=[]
    for i in range(1,len(X)+1):
        ls.append(SUMBARS_single(X[:i],A))
    return ls
#  LLVBARS求上一低点到当前的周期数。
def LLVBARS(X,N):
    if N==0:
        ls=X
    else:
        ls=X[-N:]
    return (N-1-ls.index(min(ls)))
#HHVBARS 上一高点位置    求上一高点到当前的周期数。 
def HHVBARS(X,N):
    if N==0:
        ls=X
    else:
        ls=X[-N:]
    return (N-1-ls.index(max(ls))) 
#BARSLAST 上一次条件成立位置    上一次条件成立到当前的周期数。 X为0或者1
def BARSLAST(X):
    ls=X[::-1]
    n=ls.index(1)
    return n
#BARSSINCE 第一个条件成立位置    第一个条件成立到当前的周期数。
#参数说明 X是一个含0或者1的list,
def BARSSINCE(X):
    ls=X
    n=ls.index(1)
    return len(X)-1-n
#查找条件语句成立的位置,正序 返回int 就是第一个条件成立的位置
#filter为 ==  >=  <= > <
#如，在X列表里查找>=A的值的位置，倒序  : BARSLOOKUP(X,A,filter='>=')
def BARSLOOKUP(X,A,filter='=='):
    re=float('NaN')
    if filter == '==':
        re=X.index(A)
    elif filter == '>':
        re=list(np.array(X)>A).index(True)
    elif filter == '<':
        re=list(np.array(X)<A).index(True)
    else:
        pass
    return re
#查找条件语句成立的位置,倒序 返回int 就是以最后一个数为准第一个条件成立的位置 比方返回4,就是以最
#后的数为准倒数4个位置
#filter为 ==  >  < 
#如，在X列表里查找>=A的值的位置，  : BARSLOOKUP(X,A,filter='>=')
def BARSLOOKDOWN(X,A,filter='=='):
    X=X[::-1]
    re=float('NaN')
    if filter == '==':
        re=X.index(A)
    elif filter == '>':
        re=list(np.array(X)>A).index(True)
    elif filter == '<':
        re=list(np.array(X)<A).index(True)
    else:
        pass
    return re

