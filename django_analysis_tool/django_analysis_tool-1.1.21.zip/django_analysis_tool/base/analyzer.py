#coding:utf-8
import logging

class DotableDict(dict):
    def __init__(self,*args,**kwargs):
        dict.__init__(self,*args,**kwargs)
        self.__dict__ = self

class Analyzer(object):
    #fail_detail_iterable 是个生成器，生成器是个一次性消耗品，千万记住！！！
    def __init__(self,fail_detail_iterable,device_name):
        self.data = list(fail_detail_iterable)
        self.solution = []
        self.device_name = device_name

        #将json的字段映射为用户可接受的内容
        #1: 直接判断kat运行状态
        #2：严重影响手机测试结果
        #3：轻微影响手机测试结果
        #4：平台不做统计部分
        #5: 输出到平台的判断标准
        self.map = {"KATUNINSTALL":'kat被卸载',#1
                    "KATEXCEPTION":'kat异常',#1
                    "SETTINGEXCEPTION":'setting异常',#2
                    "PHONEEXCEPTION":'phone异常',#2
                    "SYSTEMUIEXCEPTION":'systemui异常',#2
                    "SDCARDONMOUNT":'sd卡处于挂载状态',#1
                    "SDCARDSTORAGE":'sd卡剩余空间',#2
                    "PHONESTORAGE":'手机系统剩余空间',#2
                    "AMEXCEPTION":'am运行异常',#2
                    "PMEXCEPTION":'pm运行异常',#2
                    "ACTIVITY_MANAGER_EXCEPTION":"Activity管理器异常",#1
                    "ADB_OFFLINE":"ADB掉线",#2
                    "SYSTEM_CRASH":"控制台Instrumentation命令报异常",#1
                    "LUA_NO_METHOD":"Lua方法调用异常",#4(2)
                    "TOP_PROCESS_WRONG":"Top进程错误",#4(3)
                    "LUA_FILE_LOST":"Lua脚本文件丢失",#4(2)
                    "LIFE_CYCLE_SU":"SU通讯异常",#1(5)
                    "LIFE_CYCLE_INI_ENV":"Kat初始化环境异常",#1(5)
                    "LIFE_CYCLE_RUN_APP":"启动KAT失败",#1(5)
                    "LIFE_CYCLE_INSTRUMENTATION":"Instrumentation执行异常",#2
                    "LIFE_CYCLE_LUA":"Lua脚本程序未正常结束",#2
                    "LIFE_CYCLE_BRIDGE":"Bridge连接失败",#2(5)
                    "KAT_DIRECTORY_BROKEN":"Kat系统目录异常",#2
                    "SDCARD_PERMISSION_DENIED":"sd卡权限不足",#1
                    "SU_COMMAND_LOST":"手机内部SU程序丢失",#1
                    "LIBLUAJAVA_NOT_FOUND":"LibLuaJava未找到",#1
                    "KAT_KILL_9":"Kat被强杀",#1
                    "ZYGOTE_304":"Zygote抛出304异常",#2
                    "SENDKEYEVENT_PERMISSION_DENIED":"发送KeyEvent权限不足",#3
                    "ZHOOK_FAIL":"ZHook失败",#1
                    "SYS_DEAD_BY_SERVICE":"系统多服务Dead",#2
                    "READ_ONLY_FILESYSTEM":"只读文件系统",#1
                    "NOINTERCEPT":"无法拦截",#4(1)
                    "INTER_KENEL":"Intel内核",#4(1)
                    "FILESYSTEM":"文件系统问题",#4(2)
                    "NOROOT":"无法Root",#4(1)
                    "SDKLOWEST":"2.3SDK",#4(1)
                    "hasDirectory_Result":"测试后没有Result文件夹"#4(1)
                    }
        # self.map = DotableDict(self.map)

        #已知问题的特征，作为补充添加
        self.known = {'6607': self.map["NOINTERCEPT"],
                'M4': self.map["NOINTERCEPT"],
                'LA6': self.map["NOINTERCEPT"],
                'WA1': self.map["NOINTERCEPT"],
                'X5L': self.map["NOINTERCEPT"],
                'A936': self.map["NOINTERCEPT"],
                'P70-t': self.map["NOINTERCEPT"],
                'Q2': self.map["NOINTERCEPT"],
                'M2U': self.map["NOINTERCEPT"],
                'K900': self.map["INTER_KENEL"],
                '8720L': self.map["FILESYSTEM"],
                '8089': self.map["FILESYSTEM"],
                'U819': self.map["FILESYSTEM"],
                '5910': self.map["FILESYSTEM"],
                'G6-C00': self.map["FILESYSTEM"],
                'X3S': self.map["NOROOT"],
                'R7005': self.map["NOROOT"],
                'T528t': self.map["NOROOT"],
                'T329t': self.map["NOROOT"],
                '8022': self.map["SDKLOWEST"],
                '8180': self.map["SDKLOWEST"],
                '8020+': self.map["SDKLOWEST"],
                '8070': self.map["SDKLOWEST"],
                'GN100': self.map["SDKLOWEST"],
                'C510e': self.map["SDKLOWEST"],
                'C8650': self.map["SDKLOWEST"],
                'C8650+': self.map["SDKLOWEST"],
                'T619+': self.map["SDKLOWEST"],
                'A218t': self.map["SDKLOWEST"],
                'A278t': self.map["SDKLOWEST"],
                'A288t': self.map["SDKLOWEST"],
                'A308t': self.map["SDKLOWEST"],
                'A318t': self.map["SDKLOWEST"],
                'A750': self.map["SDKLOWEST"],
                'P970': self.map["SDKLOWEST"],
                'XT615': self.map["SDKLOWEST"],
                'R801': self.map["SDKLOWEST"],
                'R807': self.map["SDKLOWEST"],
                'I9050': self.map["SDKLOWEST"],
                'I9070': self.map["SDKLOWEST"],
                'I9103': self.map["SDKLOWEST"],
                'N7000': self.map["SDKLOWEST"],
                'S5830i': self.map["SDKLOWEST"],
                'S6352': self.map["SDKLOWEST"],
                'I779': self.map["SDKLOWEST"],
                'i929': self.map["SDKLOWEST"],
                'W999': self.map["SDKLOWEST"],
                'LT18i': self.map["SDKLOWEST"],
                'MT11i': self.map["SDKLOWEST"],
                'MT15i': self.map["SDKLOWEST"],
                'R800i': self.map["SDKLOWEST"],
                'ST25i': self.map["SDKLOWEST"],
                'U790':self.map["SDKLOWEST"]
                }

    def run(self):
        self.run_map()
        # self.isIntercept()
        self.run_known()
        self.data = None
        return self.solution

    def isIntercept(self):
        #1 检查手机是否可以被kat拦截
        logging.info(str(self.data))
        if ('LIFE_CYCLE_SU' not in self.data) and \
                ('LIFE_CYCLE_INI_ENV' not in self.data) and \
                ('LIFE_CYCLE_RUN_APP' not in self.data) and \
                ('LIFE_CYCLE_BRIDGE' in self.data):
            if self.map["NOINTERCEPT"] not in self.solution:
                self.solution.append(self.map["NOINTERCEPT"])

    def run_map(self):
        mapped = [self.map[key] for key in self.data if key in self.map]
        self.solution.extend(mapped)

    def run_known(self):
        for name, problem in self.known.iteritems():
            if name in self.device_name:
                if problem not in self.solution:
                    self.solution.append(problem)

