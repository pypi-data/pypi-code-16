# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 13:16:34 2016

@author: doarni
"""

import lxml.html as Lhtml

class parse():
        
    def returnClassName(htmlData, path, indexNumber): #return class at given list index
        html = Lhtml.fromstring(htmlData)
        list = html.cssselect(path)
        return list[indexNumber].get('class')
        
    def returnClassData(htmlData, path): #return classes as a dictionary
        html = Lhtml.fromstring(htmlData)
        list = html.cssselect(path)
        classes = []
        for i in len(list):
            classes.append(list[i].get('class'))
        return {'path': path, 'data': classes}

    def returnInfo(htmlData, path, indexNumber, selectorType): #return list of data at end of path
        html = Lhtml.fromstring(htmlData)
        list = html.cssselect(path)
        return list[indexNumber].get(selectorType)
        
    def returnTextInfo(htmlData, path):
        html = Lhtml.fromstring(htmlData)
        list = html.cssselect(path)
        for item in list:           
            return [item.text_content(),item.get('value')]
    