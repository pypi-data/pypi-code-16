# coding:utf-8
import pytz
from datetime import datetime


def test():
    print 'hello world'


def convert_tz(utc_time_str, tz='Asia/Shanghai', type='str'):
    '''
    将存储在数据库中的UTC时间转换成指定时间
    :param utc_time_str:字符串格式的0时区时间
    :param tz: 目标时区
    :param type: 返回结果的格式  str,dt
    :return: 目标目标时间
    '''
    utc_datetime = datetime.strptime(utc_time_str, "%Y-%m-%d %H:%M:%S")

    current_tz = pytz.timezone(tz)
    utc_tz = pytz.timezone('UTC')
    utc_tz_datetime = utc_tz.localize(utc_datetime, is_dst=None)
    value = utc_tz_datetime.astimezone(current_tz)

    if type == 'str':
        return value.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return value


if __name__ == '__main__':
    print 'test ...'
    test()
