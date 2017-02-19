#!/usr/bin/env python

import json
import requests

class youdao:
    __KEY = ""
    __KEY_FROM = ""
    __URL = "http://fanyi.youdao.com/openapi.do"
    __DOC_TYPE = "json"

    def __init__(self, KEY, KEY_FROM):
        self.__KEY = KEY
        self.__KEY_FROM = KEY_FROM		


    def getUrl(self, url, keyfrom, key, doctype, q):
        tempUrl = "{url}?keyfrom={keyfrom}" \
                "&key={key}&type=data&doctype={doctype}&version=1.1" \
                "&q={q}".format(url=url, keyfrom=keyfrom,
                        key=key, doctype=doctype, q=q)
        return tempUrl


    def getContent(self, url):
        return requests.get(url).text


    def getTranslation(self, jsonObj):
        result = ""
        translations = jsonObj['translation']
        for translation in translations:
            result += translation + "\r\n"
        return result[0:-2]


    def getUSPhonetic(self, jsonObj):
        try:
            usPhonetic = jsonObj['basic']['us-phonetic']
        except:
            usPhonetic = ""
        return usPhonetic


    def getPhonetic(self, jsonObj):
        try:
            phonetic = jsonObj['basic']['phonetic']
        except:
            phonetic = ""
        return phonetic


    def getUKPhonetic(self, jsonObj):
        try:
            usPhonetic = jsonObj['basic']['uk-phonetic']
        except:
            usPhonetic = ""
        return usPhonetic


    def getExplains(self, jsonObj):
        try:
            explain = jsonObj['basic']['explains']
            return explain
        except:
            print("[Err] : No result")
            exit(1)


    def getWeb(self, jsonObj):
        return jsonObj['web']


    def getMax(self, numbers):
        maxNumber = 0
        for number in numbers:
            if number > maxNumber:
                maxNumber = number
        return maxNumber


    def getExplains(self, jsonObj):
        try:
            explain = jsonObj['basic']['explains']
            return explain
        except:
            print("[Err] : No result")
            exit(1)


    def getWeb(self, jsonObj):
        return jsonObj['web']


    def getMax(self, numbers):
        maxNumber = 0
        for number in numbers:
            if number > maxNumber:
                maxNumber = number
        return maxNumber


    def printResult(self, translation, usPhonetic, phonetic, ukPhonetic, explains, webs):
        maxLength = 16
        print("{separator}翻译{separator}".format(separator='-'*maxLength))
        print(translation)
        print("{separator}音标{separator}".format(separator='-'*maxLength))
        if phonetic:
            print("[" + phonetic + "]")
        if usPhonetic:
            print("[{" + usPhonetic + "] (US)")
        if ukPhonetic != "":
            print("[" + ukPhonetic + "] (UK)")
        print("{separator}解释{separator}".format(separator='-'*maxLength))
        for explain in explains:
            print(explain)
        print("{separator}网络{separator}".format(separator='-'*maxLength))
        for web in webs:
            print(web['key'])
            values = web['value']
            for value in values:
                print("    " + value)


    def trans(self, word):
        tempUrl = self.getUrl(self.__URL, self.__KEY_FROM, self.__KEY, self.__DOC_TYPE, word);
        content = self.getContent(tempUrl)
        jsonObj = json.loads(content)
        translation = self.getTranslation(jsonObj)
        usPhonetic = self.getUSPhonetic(jsonObj)
        phonetic = self.getPhonetic(jsonObj)
        ukPhonetic = self.getUKPhonetic(jsonObj)
        explains = self.getExplains(jsonObj)
        webs = self.getWeb(jsonObj)
        self.printResult(translation, usPhonetic, phonetic, ukPhonetic, explains, webs)
