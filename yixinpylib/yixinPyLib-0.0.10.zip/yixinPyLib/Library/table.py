#-_- coding:UTF-8
'''
Created on 2016年11月2日

@author: wuyunpeng
'''


class Table:
    def __init__(self,driver):
        self.driver = driver
        
    def getCellText(self,table,row,col):
        '''获取table单元格中对象文本
        入参：
        @table 传入table的定位
        @row  传入要获取的行号，包括标题，从0开始
        @col  传入要获取的列号，从1开始'''
        rows = table.find_elements_by_tag_name("tr")
        therow = rows[row]
        if len(therow.find_elements_by_tag_name("th"))>0:
            cells = therow.find_elements_by_tag_name('th')
            text1 = cells[col-1].text
        if len(therow.find_elements_by_tag_name("td"))>0:
            cells = therow.find_elements_by_tag_name("td")
            text1 = cells[col-1].text
        print text1
        return text1
    def getCellObj(self,table,row,col):  
        '''获取table单元格中   对象object
        入参：
        @table 传入table的定位
        @row  传入要获取的行号，包括标题，从0开始
        @col  传入要获取的列号，从1开始'''
        rows = table.find_elements_by_tag_name("tr")
        therow = rows[row]
        if len(therow.find_elements_by_tag_name("th"))>0:
            cells = therow.find_elements_by_tag_name('th')
            obj = cells[col-1]
        if len(therow.find_elements_by_tag_name("td"))>0:
            cells = therow.find_elements_by_tag_name("td")
            obj = cells[col-1]
        return obj
    def getrowsno(self,table):
        '''获取table的行数'''
        rows = table.find_elements_by_tag_name("tr")
        return rows