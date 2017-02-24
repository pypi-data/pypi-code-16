from bauzak.Modbus控制器 import Modbus控制器
from fatek.target import FatekTarget


class Modbus試驗(Modbus控制器):

    'https://github.com/rimek/fatek-fbs-lib/blob/master/fatek/symbol.py'
    Fatek_PLC_offset = {
        'Y': 0,
        'X': 1000,
        'M': 2000,
        'S': 6000,
        'T': 9000,
        'R': 0,
        'D': 6000,
        'C': 9500
    }

    def __init__(self, ip, port, 對應表):
        super(Modbus試驗, self).__init__(ip, port)
        self.對應表 = 對應表

    def __getattr__(self, name):
        位址 = self.對應表[name]
        return FatekTarget(self.連線, 位址).read()

    def __setattr__(self, name, value):
        if name in ["連線", "對應表"]:
            return super(Modbus試驗, self).__setattr__(name, value)
        位址 = self.對應表[name]
        FatekTarget(self.連線, 位址).write(value)
        return
