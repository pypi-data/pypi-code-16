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
        
        # default host and port
        host = 'localhost'
        port = '5800'
        self.api = 'http://'+ host + ':' + port + '/nudb/'
        self.db = 'test'

    def connect(self, host, port, db):
        self.api = 'http://'+ host + ':' + port + '/nudb/'
        self.db = db
        print('API: %s, db: %s' % (self.api, self.db))

    def rput(self, data, kind, *recBeg):
        """ kind: json/text """
        url = self.api + 'rput'
        
        if kind == 'text':
            if len(recBeg) == 1:
                opts = {
                    'db': self.db,
                    'data': json.dumps(data),
                    'recbeg': recBeg[0],
                    'format': kind
                }
            else:
                return 'Wrong recBeg'
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
        url = self.api + "fput"

        fileData = {
            'file': codecs.open(filePath, 'rb', 'utf-8')
        }

        if kind == 'text':
            if len(recBeg) == 1:
                opts = {
                    'db': self.db,
                    'recbeg': recBeg[0],
                    'format': kind
                }
            else:
                return 'Wrong recBeg'
        elif kind == 'json':
            opts = {
                'db': self.db,
                'format': kind
            }
        else:
            return 'Wrong format'

        #print('fput options: %s' % opts)
        #print(fileData)
        res = requests.post(url, opts, files=fileData)
        print('fput response: %s' % res.status_code)
        return res.text

    def rget(self, rid):
        url = self.api + "rget"
        
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
        url = self.api + "rdel"
        
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
        url = self.api + "query"
        
        opts = {
            'db': self.db,
            'q': query,
            'out': 'json'
        }
        
        #print('search options: %s' % opts)
        res = requests.get(url, opts)
        print('search response: %s' % res.status_code)
        return res.text

