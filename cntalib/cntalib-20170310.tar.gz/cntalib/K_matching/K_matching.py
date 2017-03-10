# -*- coding: utf-8 -*-
"""
K线形态匹配类函数

@author: jianxue
"""
import cntalib
import pandas as pd
import numpy as np


def GETPRICE(X):
    #取得X列表中相临两个数之间的涨幅 返回一个numpy.array
    re=np.diff(X)/X[:-1]*100
    return(re)

def ZTPRICE(X,N,filter=9.98):
    #返回N周期内有多少个涨幅大于filter以上的 涨停filter=9.98
    X=X[:N]
    zt=cntalib.GETPRICE(X)>filter
    #返回非0的个数
    return zt.sum()

def DTPRICE(X,N,filter=-9.98):
    #返回N周期内有多少个涨幅小于filter以上的 跌停filter=-9.98
    X=X[:N]
    zt=cntalib.GETPRICE(X)<filter
    #返回非0的个数
    return zt.sum()

def ZTONEPRICE(C,H,L,N,filter=9.95):
    #返回N周期内有多少个一字涨停
    zflist=(np.diff(C)/C[:-1]*100)>filter
    Z=(np.array(H)/np.array(L))[:-1]==1
    re=Z*zflist
    return re.sum()

def DTONEPRICE(C,H,L,N,filter=-9.95):
    #返回N周期内有多少个一字跌停
    zflist=(np.diff(C)/C[:-1]*100)<filter
    Z=(np.array(H)/np.array(L))[:-1]==1
    re=Z*zflist
    return re.sum()


