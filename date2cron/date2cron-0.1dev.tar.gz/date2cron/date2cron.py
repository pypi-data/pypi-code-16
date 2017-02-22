#!/usr/bin/env python
#coding:utf-8
"""
  Author:  cat --<yafeile@sohu.com>
  Purpose: 
  Created: 2017/2/21
"""

def date_to_cron(year=None, month=None,day=None,hour=None,minute=None,week=None):
    """
    将日期转换为Cron表达式,https://en.wikipedia.org/wiki/Cron
    >>> date_to_cron()
    '* * * * * *'
    >>> date_to_cron(month=2,day=21,hour=10,minute=21)     #2月21号早上10:21分
    '21 10 21 2 * *'
    >>> date_to_cron(month=2,hour=10,minute=21,week=(0,3)) #2月每个星期天和星期三早上10:21分
    '21 10 * 2 0,3 *'
    >>> date_to_cron(month=2,hour=10,minute=21,day=[1,5])  #2月1号到5号早上10:21分
    '21 10 1-5 2 * *'
    >>> date_to_cron(month=2,hour=10,minute=[21,55],day=[1,5]) #2月1到5号早上10点21分到55分
    '21-55 10 1-5 2 * *'
    """
    date_arr = [minute, hour, day, month, week, year]
    for i, d in enumerate(date_arr):
        if not d:
            date_arr[i] = '*'
        else:
            if isinstance(d, tuple):
                d = ','.join(str(x) for x in d)
            elif isinstance(d, list):
                d = '-'.join(str(x) for x in d)
            date_arr[i] = str(d)
    expr = ' '.join(date_arr)
    return expr


def main():
    date_to_cron()
    date_to_cron(month=2,day=21,hour=10,minute=21)
    date_to_cron(month=2,hour=10,minute=21,week=(0,3))
    date_to_cron(month=2,hour=10,minute=21,day=[1,5])
    date_to_cron(month=2,hour=10,minute=[21,55],day=[1,5])

if __name__ == '__main__':
    main()