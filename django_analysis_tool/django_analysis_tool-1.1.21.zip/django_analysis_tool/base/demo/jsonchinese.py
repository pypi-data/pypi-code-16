#coding:utf-8

import json,sys
c = [{"live": [[0, "kat被卸载"]], "keyword": "KATUNINSTALL"}, {"live": [[0, "kat异常"]], "keyword": "KATEXCEPTION"}, {"live": [[0, "setting异常"]], "keyword": "SETTINGEXCEPTION"}, {"live": [[0, "phone异常"]], "keyword": "PHONEEXCEPTION"}, {"live": [[0, "systemui异常"]], "keyword": "SYSTEMUIEXCEPTION"}, {"live": [[0, "sd卡处于挂载状态"]], "keyword": "SDCARDONMOUNT"}, {"live": [[0, "sd卡剩余空间"]], "keyword": "SDCARDSTORAGE"}, {"live": [[0, "手机系统剩余空间"]], "keyword": "PHONESTORAGE"}, {"live": [[0, "am运行异常"]], "keyword": "AMEXCEPTION"}, {"live": [[0, "pm运行异常"]], "keyword": "PMEXCEPTION"}]
f = open(r"d:\accessmanager_json",'w')
json.dump(c,f,ensure_ascii=False,encoding='utf-8')
f.close()
with open(r"C:\Users\SJKP\Desktop\autoTest_logcat.txt",'r') as logcat:
    content = logcat.read()
with open(r"d:\accessmanager_json",'r') as ff:
    load_out1 = json.load(ff,encoding='utf-8')
    for d in load_out1:
        for key,value in d['live']:
            value = value.encode(sys.getfilesystemencoding())
            if content.find(value)!=-1:
                print 1
