# -*- coding: utf-8 -*-

import os, sys
import codecs
import json
import logging
import requests

class NuDB(object):

    def __init__(self):
        reload(sys)
        sys.setdefaultencoding("utf-8")
        
        self.host = 'localhost'
        self.db = 'test'

    def connect(self, host, db):
        self.host = host
        self.db = db
        print('Connect to: %s, db: %s' % (self.host, self.db))

    def rput(self, data, kind, *recBeg):
        """ kind: json/text """
        url = self.host + 'rput'
        if kind == 'text':
            opts = {
                'db': self.db,
                'data': json.dumps(data),
                'recBeg': recBeg,
                'format': kind
            }
        elif kind == 'json':
            opts = {
                'db': self.db,
                'data': json.dumps(data),
                'format': kind
            }
        else:
            return 'Wrong format'

        #print('rput options: %s' % opts)
        res = requests.post(url, opts)
        print('rput response: %s' % res.status_code)
        return res.text
    
    def fput(self, filePath, kind, *recBeg):
        """ kind: json/text """
        url = self.host + "fput"

        fileData = {
            'file': codecs.open(filePath, 'r', 'utf-8')
        }

        if kind == 'text':
            opts = {
                'db': self.db,
                'recBeg': recBeg,
                'format': kind
            }
        elif kind == 'json':
            opts = {
                'db': self.db,
                'format': kind
            }
        else:
            return 'Wrong format'

        #print('fput options: %s' % opts)
        res = requests.post(url, data=opts, files=fileData)
        print('fput response: %s' % res.status_code)
        return res.text
    
    def rget(self, rid):
        url = self.host + "rget"
        
        opts = {
            'db': self.db,
            'rid': rid,
            'out': 'json'
        }
        
        #print('rget options: %s' % opts)
        res = requests.get(url, opts)
        print('rget response: %s' % res.status_code)
        return res.text

    def rdel(self, rid):
        url = self.host + "rdel"
        
        opts = {
            'db': self.db,
            'rid': rid,
            'out': 'json'
        }
        
        #print('rdel options: %s' % opts)
        res = requests.post(url, opts)
        print('rdel response: %s' % res.status_code)
        return res.text
    
    def search(self, query):
        url = self.host + "query"
        
        opts = {
            'db': self.db,
            'q': query,
            'out': 'json'
        }
        
        #print('search options: %s' % opts)
        res = requests.get(url, opts)
        print('search response: %s' % res.status_code)
        return res.text

