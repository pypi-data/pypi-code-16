#-*-encoding=utf8-*-
"未知交易错误"
class UnknownTradeException(Exception):pass
"机会消失"
class ChanceOverException(Exception):pass
"对冲结束"
class HedgeEndException(Exception):pass
"检查到掉线引发的异常"
class DownlineExcpetion(Exception):
    def __init__(self,inst=None):
        self.inst=inst
"系统正在维护"
class SysMaintenanceExcpetion(Exception):pass
"用户被屏蔽"
class UserBlockedExcpetion(Exception):pass
"用户终止程序"
class StopAppException(Exception):pass
"查询赌吃票数据失败"
class FetchBetDataFailException(Exception):pass
"交易信用额不够异常"
class NotEnoughBalanceException(Exception):pass

if __name__ == '__main__':
    pass
