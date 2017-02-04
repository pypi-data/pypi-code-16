#!/usr/bin/env python
# coding=utf-8
import os,pickle
import numpy as np
import pandas as pd
import datetime
from datetime import timedelta
import requests

__author__ = 'Xiaowei Yan'
__version__ = '1.0'

__all__ = ['tick']




class tick(object):


    def __init__(self,ticker,past=15):
        self.ticker = ticker
        self.past = past



    def get_tick(self,interval = 60):
        url = 'https://www.google.com/finance/getprices?i='+str(interval)+'&p='+str(self.past)+'d&f=d,o,h,l,c,v&df=cpct&q='+self.ticker
        page = requests.get(url).text.split('\n')
        page = page[7:-1]
        po = [page.index(x) for x in page if 'a' in x]
        sec = []
        for i in range(len(po)):
            try:
                sec.append(page[po[i]:po[i+1]])
            except:
                sec.append(page[po[i]:])
        return sec


    def day(self,number,interval = 60):
        page = self.get_tick(interval)
        df = page[-number]
        price = []
        vol = []
        time = []
        for i in range(len(df)):
            price.append(df[i].split(',')[1])
            vol.append(df[i].split(',')[-1])
            time.append((df[i].split(',')[0]))
        time[0] = '0'
        time = map(int,time)
        price,vol = map(float,price),map(float,vol)
        out = pd.DataFrame({'price':price,'vol':vol,'time':time})
        out = out.set_index('time')
        return out
