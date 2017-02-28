# coding:utf-8
import pytz
from datetime import datetime


def test():
    print 'hello world'


def convert_tz(utc_time_str, tz='Asia/Shanghai'):
    # 将存储在数据库中的UTC时间转换成指定时间
    utc_datetime = datetime.strptime(utc_time_str, "%Y-%m-%d %H:%M:%S")

    current_tz = pytz.timezone(tz)
    utc_tz = pytz.timezone('UTC')
    utc_tz_datetime = utc_tz.localize(utc_datetime, is_dst=None)
    value = utc_tz_datetime.astimezone(current_tz)

    return value.strftime("%Y-%m-%d %H:%M:%S")


if __name__ == '__main__':
    print 'test ...'
    test()
