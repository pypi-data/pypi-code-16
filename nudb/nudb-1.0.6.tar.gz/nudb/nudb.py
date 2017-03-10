# -*- coding: utf-8 -*-

import os, sys
import re
import codecs
import json
import requests
import tools

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

        if data == "":
            return 'Empty data'

        if kind == 'text' and isinstance(data, str):
            if len(recBeg) == 1:
                data = re.sub('\\\\\\\\','\\\\', data)
                opts = {
                    'db': self.db,
                    'data': data,
                    'recbeg': recBeg[0],
                    'format': kind
                }
            else:
                return 'Wrong recBeg'
        elif kind == 'json':
            check = tools.check_JSON(data)
            if check == 1:
                # JSON object
                opts = {
                    'db': self.db,
                    'data': json.dumps(data),
                    'format': kind
                }
            elif check == 2:
                # JSON string
                opts = {
                    'db': self.db,
                    'data': data,
                    'format': kind
                }
            else:
                return 'Invalid JSON format'
        else:
            return 'Wrong format'

        res = requests.post(url, opts)
        print('[rput] Response: %s' % res.status_code)
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

        res = requests.post(url, opts, files=fileData)
        print('[fput] Response: %s' % res.status_code)
        return res.text

    def rget(self, rid):
        url = self.api + "rget"
        
        opts = {
            'db': self.db,
            'rid': rid,
            'out': 'json'
        }
        
        res = requests.get(url, opts)
        print('[rget] Response: %s' % res.status_code)
        return res.text

    def rdel(self, rid):
        url = self.api + "rdel"
        
        opts = {
            'db': self.db,
            'rid': rid,
            'out': 'json'
        }
        
        res = requests.post(url, opts)
        print('[rdel] Response: %s' % res.status_code)
        return res.text
    
    def rupdate(self, rid, data, kind):
        """ kind: json/text """
        url = self.api + "rupdate"
        record = ""
        
        if rid == "":
            return 'Empty rid'
        if data == "":
            return 'Empty data'

        if kind == 'text' and isinstance(data, str):
            record = re.sub('\\\\\\\\','\\\\', data)
            opts = {
                'db': self.db,
                'getrec': 'n',
                'out': 'json',
                'rid': rid,
                'record': record
            }
            res = requests.post(url, opts)
            print('[rupdate] Response: %s' % res.status_code)
            return res.text

        elif kind == 'json':
            """ Use rdel + rput, because rupdate of JSON format is currently not supported."""
            check = tools.check_JSON(data)
            
            if check >= 1:
                # rdel
                res = self.rdel(rid)
                obj = json.loads(res)
                
                if 'error' not in obj['result'][0].keys():
                    # delete successful -> rput
                    res = self.rput(data, kind)
                return res
            else:
                return 'Invalid JSON format'
        else:
            return 'Wrong format'
                
    def search(self, query):
        url = self.api + "query"
        
        opts = {
            'db': self.db,
            'q': query,
            'out': 'json'
        }
        
        res = requests.get(url, opts)
        print('[search] Response: %s' % res.status_code)
        return res.text

