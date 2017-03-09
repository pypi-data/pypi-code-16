#coding:utf-8
__author__ = 'creeper'

import xlwt,os

class xls:
    def __init__(self,devices,path = r"d:\dst_path"):
        self.styleBlueBkg = xlwt.easyxf('pattern: pattern solid, fore_colour ocean_blue; font: bold on;')
        self.red = xlwt.easyxf('pattern: pattern solid, fore_colour red;')
        self.green = xlwt.easyxf('pattern: pattern solid, fore_colour green;')
        self.gray = xlwt.easyxf('pattern: pattern solid, fore_colour gray40;')
        self.path = path
        self.devices = devices
        self.titles = self._getTitle()
        self.first_col = []
        os.chdir(path)
        self.xls_file = xlwt.Workbook()
        self.newSheet()


    def _getTitle(self):
        titles = []
        for device_info in self.devices:
            for item in device_info.keys():
                if item not in titles:
                    titles.append(item)
        return titles

    def newSheet(self):
        self.sheet = self.xls_file.add_sheet('main',cell_overwrite_ok=True)
        self.sheet.write(0,0,'device')
        self.titles.remove('device')
        self.titles.sort()
        for title in self.titles:
            self.sheet.write(0,self.titles.index(title)+1,title,self.gray)

    def enterValue(self):
        for device_info in self.devices:
            self.first_col.append(device_info['device'])
            self.sheet.write(len(self.first_col),0,device_info['device'],self.gray)
            for key in device_info.keys():
                if not key == 'device':
                    ncol = self.titles.index(key)+1
                    nrow = len(self.first_col)
                    value = device_info[key]
                    self.drawColor(nrow,ncol,key,value)

    def drawColor(self,nrow,ncol,key,value):
        if value:
            self.sheet.write(nrow,ncol,value,self.green)
        else:
            self.sheet.write(nrow,ncol,value,self.red)

    def save(self,name = "Metrix.xls"):
        self.xls_file.save(name)

class LightXls():
    def __init__(self,iters):
        self.xls_file = xlwt.Workbook()
        self.sheet = self.xls_file.add_sheet('main',cell_overwrite_ok=True)
        self.sheet.write(0,0,'device')
        self.iters = iters

    def enterValue(self):
        for index ,device in enumerate(self.iters):
            self.sheet.write(index+1,0,device)

    def save(self,name = "metrix.xls"):
        self.xls_file.save(name)

def parseSourceDevicesList(iters):
    tmp = []
    for device in iters:
        tmp.append(device.split("_")[-2].split(" ")[-1])
    return tmp

def parseUserDevicesList(s):
    l = s.split("、")
    tmp = []
    for i in l:
        tmp.append(i.strip().split(" ")[-1])
    return tmp


if __name__ == "__main__":
    os.chdir(r"C:\Users\SJKP\Desktop")

    # tmp = []
    # file = open(r"C:\Users\SJKP\Desktop\1.txt")
    # for line in file.readlines():
    #     tmp.append(line)
    # l = parseSourceDevicesList(tmp)



    s = "Samsung GT-N7100、Xiaomi mi-one-c1、HUAWEI G750-T00 、Sony MT15i、HTC C510e、Samsung GT-I9508、Coolpad 8190、Coolpad 5910、 HUAWEI C8650+ 、Samsung SM-G7108、Samsung GT-S7568I、Coolpad 9190L、OPPO R7007、 HUAWEI G525-U00、AMOI N821、HUAWEI B199、HTC M8d、Samsung GT-I9300I、Samsung SM-G7109、HUAWEI MT7-TL00、Samsung SM-G3502C、BBK vivo Y613F、Coolpad 8730L、OPPO R8107、OPPO R8107、LENOVO A938t、ZTE Q505T、Xiaomi MI 3W、Huawei C8817D、Samsung SM-G5108Q、Coolpad Y80D、DOOV S2y、Motorola XT1033、DOOV L3C、vivo X710L、Samsung SCH-i929、Huawei C199、vivo Y13L、vivo Y29L、Huawei Y516-T00、Samsung SM-G3589W、DAQ _Q2、SUGAR SS136、Philips W8355、LENOVO K30-T、GiONEE GN706L、DOOV D330、GiONEE E7、Coolpad 7251 、Xiaomi 2013023、ZTE N918St、Coolpad 5950、Sony L50u、Huawei P6 S-U06、vivo Y913、BBK vivo Y28L、vivo Y23L、CMDC M812C、Samsung SM-G3559、OPPO R8200、GiONEE E3T、HUAWEI C8816D、Samsung Galaxy Nexus、Samsung GT-I9500、Coolpad 8720L、vivo Y627、Sony LT18、Samsung GT-I9103、Sony R800i、Huawei C8650、Coolpad 8180、 Lenovo A278t、Samsung SCH-I779、Lenovo A750、Coolpad 8150D、 CoolPad8070、Samsung GT-I9070、Samsung GT-I9050、Samsung SCH-W999、LG -P970、 HUAWEI C8813DQ、OPPO R807、 Lenovo A218t、Sony MT11i 、 CoolPad 8020+、DOOV D360、Sony ST25i、Samsung GT-N7000、Lenovo A308t、HUAWEI G6-C00、HUAWEI G730-C00、OPPO R801、K-Touch T619+、Coolpad 8022、LENOVO A288t、Huawei G716-L070、Motorola XT615、Newman K2"
    l = parseUserDevicesList(s)

    mLXls = LightXls(l)
    mLXls.enterValue()
    mLXls.save("source.xls")




