# -*- coding: utf-8 -*-
import math
from pymongo import MongoClient

class PMI(object):
    """docstring for PMI"""
    def __init__(self, uri=None):
        self.client = MongoClient(uri)
        self.db = self.client['nlp']
        self.Collect = self.db['pmi']
        self.frequency = {}

    def checkHasPMI(self, keyword):
        # check if it already has PMI result or not
        # if not, need to calculate at first time.
        # if already has PMI, then just query it in mongoDB, it will save alot of times.
        result = self.Collect.find({'key':keyword}, {'freq':1, 'value':1, '_id':False}).limit(1)
        if result.count() == 0:
            return False
        elif list(result)[0]['value'] == []:
            return False
        return True

    def getWordFreqItems(self):
        # result all frequency of word in type of dict.
        self.frequency = {}
        for i in self.db['kcm'].find():
            keyword = i['key']
            for correlationTermsArr in i['value']:
                corTermCount = correlationTermsArr[1]

                # accumulate keyword's frequency.
                self.frequency[keyword] = self.frequency.setdefault(keyword, 0) + corTermCount

        return self.frequency.items()

    def build(self):
        import pymongo
        self.Collect.remove({})

        # read all frequency from KCM and build all PMI of KCM in MongoDB. 
        # with format {key:'中興大學', freq:100, value:[(keyword, PMI-value), (keyword, PMI-value)...]}
        result = []
        for keyword, keyword_freq in self.getWordFreqItems():
            pmiResult = []

            for kcm_pair in list(self.db['kcm'].find({'key':keyword}, {'value':1, '_id':False}).limit(1))[0]['value']:
                kcmKeyword, kcmCount = kcm_pair[0], kcm_pair[1]

                # PMI = log2(p(x, y)/p(x)*p(y)) 
                # frequency of total keyword = 154451970
                # p(x, y) = frequency of (x, y) / frequency of total keyword.
                # p(x) = frequency of x / frequency of total keyword.
                value=(math.log10( int(kcmCount) * 154451970  /(float(keyword_freq) * int(self.frequency[kcmKeyword])  )) / math.log10(2))

                # this equation is contributed by 陳聖軒. 
                # contact him with facebook: https://www.facebook.com/henrymayday
                value*=(math.log10(int(self.frequency[kcmKeyword]))/math.log10(2))

                pmiResult.append((kcmKeyword, value))

            pmiResult = sorted(pmiResult, key = lambda x: -x[1])
            result.append({'key':keyword, 'freq':keyword_freq, 'value':pmiResult})

        self.Collect.insert(result)
        self.Collect.create_index([("key", pymongo.HASHED)])

    def get(self, keyword, amount):
        # return PMI value of this keyword
        # if doesn't exist in MongoDB, then return [].

        if self.checkHasPMI(keyword):
            return list(self.Collect.find({'key':keyword}, {'value':1, '_id':False}).limit(1))[0]['value'][:amount]
        return []

if __name__ == '__main__':
    p = PMI()
    p.build()
    print(p.get("綠委", 10))