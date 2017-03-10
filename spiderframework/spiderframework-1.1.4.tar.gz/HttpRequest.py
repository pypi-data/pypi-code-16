#coding:utf-8
from datetime import datetime
import logging
import requests
import json
import time
import os
def ghNetWork(RequestModel):
    call = RequestModel('')
    headers,data,httpPost = headerAndBody()
    _result = requests.post(call.api(), headers=headers,data=data) if httpPost else requests.get(call.api(), headers=headers,data=data)
    call.response(_result)

def headerAndBody():
    if not os.path.exists('data'):
        print('not have data file')
        return '','',''
    f = open('data','r')
    lines = f.readlines()
    f.close()
    httpPost = True
    header = {}
    params = ''
    cookies = '' 
    body = ''
    for index in range(len(lines)): 
        ii = lines[index].split(':',1)
        if len(ii) == 2 and not ii[0]=='':
                if ii[0] == 'cookie':
                    cookies += ii[1].strip() + ';'
                    continue
                key = ii[0]
                value = ii[1].strip()
                header[key] = value
        header['cookie'] = cookies
        if index == 0:
            if 'POST' in lines[index]:
                print('Post Request')
                # Get body 
                httpPost = True
            else:
                print('Get Request')
                httpPost = False
                params = lines[index].split(' ')[1]
        if httpPost and index == len(lines) -1:
            body = lines[index]
            
    return header,params if not params == '' else body,httpPost
if __name__ == '__main__':
    headers,params,httpPost = headerAndBody()
    print headers,params,httpPost
    # for (k,v) in headers.items():
    #      print(str(i) + " " + params)
   