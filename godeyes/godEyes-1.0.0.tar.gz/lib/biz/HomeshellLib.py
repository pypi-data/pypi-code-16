# coding:utf-8
'''
Created on 2017年01月05日

@author: shenlang
'''

from common.Cli import Cli
import xml.etree.ElementTree as ET
from common.Validator import validator

 
class HomeshellLib(Cli): 
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def getSelectedViewText(self, ip = None,**kwargs):
        xml_sz = self.getHxml(ip)
        assert xml_sz != '', 'dump失败'
        tree = ET.fromstring(xml_sz)
        text = ''
        for elem in tree.iter(tag='node'):
            if elem.attrib['selected'] == 'true':
                if elem.attrib['text']!='':
                    text = text+ elem.attrib['text'] + ' '
        text=text.strip()
        assert text != "", "当前选中控件无文字"
        validator.validate(text, **kwargs)
        return str(text)
# 
# def aaa():
#     Cli.getUUID()
if __name__ == '__main__':
    l = HomeshellLib('192.168.0.105')
    print l.getSelectedViewText()
