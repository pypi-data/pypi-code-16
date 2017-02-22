# _*_ coding:utf-8 _*_

import os, csv

par = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))+"\\TempData\\"


def __open_csv(file_name):
    """判断文件是否存在，不存在直接打印报错信息"""
    try:
        with open(par+file_name, "r") as csv_file:
            return csv_file.readlines()
    except Exception as e:
        print "error info: ", e


def read_csv_rows(file_name):
    """读取csv文件，按行读组合成列表,如果csv没有数据返回没有数据提交,要传文件名称"""
    if __open_csv(file_name):
        read = csv.reader(__open_csv(file_name))
        list1 = []
        for i in read:
            list1.append(i)
        return list1
    else:
        return u"文件里没有数据"

