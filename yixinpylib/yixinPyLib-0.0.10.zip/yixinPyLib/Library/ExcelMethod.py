# _*_ coding:utf-8 _*_
import xlrd
import os

par = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))+"\\TempData\\"


def __open_excel(file_name):
    """判断文件是否存在，不存在直接打印报错信息"""
    try:
        data = xlrd.open_workbook(par+file_name)
        return data
    except Exception as e:
        print "error info:", e


def read_excel_rows(file_name, by_name='Sheet1', colname_index=0):
    """读取excel,文件不存在返回错误信息，按行读组合成列表，如果excel没有数据返回None
    需要传文件名称以及sheet页的名称"""
    data = __open_excel(file_name)
    table = data.sheet_by_name(by_name)
    # 获取总行数
    rows = table.nrows
    read_list = []
    if rows:
        for row_num in range(rows):
            row = table.row_values(row_num)
            read_list.append(row)
        return read_list
    else:
        return u"文件里没有数据"













