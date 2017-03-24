# coding=utf8
import calendar

import datetime
import time


def get_now_datetime():
    """
    获取当前时间date对象
    """
    t = datetime.datetime.now()
    return t


def get_now_timestamp():
    """
    获取当前时间戳
    :return:
    """
    return int(time.time())


def get_now_date():
    """
    获取当前时间date对象
    """
    t = get_now_datetime().date()
    return t


def get_now_time_str():
    """
    获取当前时间字符串 格式 "2010-10-10 12:59:40"
    """

    t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return t


def get_time_str_before(days):
    """
    获取当前时间以前某天的时间字符串 格式 "2010-10-10 12:59:40"
    """

    time_delta = datetime.timedelta(days=days)

    t = (datetime.datetime.now() - time_delta).strftime("%Y-%m-%d %H:%M:%S")

    return t


def get_now_date_str():
    """
    获取当前日期字符串 格式"2010-10-10"
    """
    t = datetime.datetime.now().strftime("%Y-%m-%d")

    return t


def get_date_str_before(days):
    """
    获取当前时间以前某天的时间字符串 格式 "2010-10-10"
    """

    time_delta = datetime.timedelta(days=days)

    t = (datetime.datetime.now() - time_delta).strftime("%Y-%m-%d")

    return t


def get_chinese_date_str(date_str):
    """
    把 yyyy-mm-dd 转成 yyyy年mm月dd日
    """

    tmp = date_str.split("-")

    year = tmp[0]
    month = tmp[1]
    day = tmp[2]

    result = u"%s年%s月%s日" % (year, month, day)

    return result


def add_months(dt, months):
    month = dt.month - 1 + months
    year = dt.year + month / 12
    month = month % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def get_month_total_days(date):
    """
    获取一个月有多少天
    :param date:
    :return:
    """
    return calendar.monthrange(date.year, date.month)[1]


def diff_seconds(date1, date2):
    """
    两个日期之间相差的秒数，存在正负
    :param date1: 小时间
    :param date2: 大时间
    :return:
    """
    timedelta = date2 - date1
    return timedelta.days * 24 * 3600 + timedelta.seconds


def parse_date(date_str):
    """
    解析日期字符串，风格为：%Y-%m-%d

    :param date_str:
    :return:
    """
    return parse(date_str, '%Y-%m-%d')


def parse_datetime(date_str):
    """
    解析日期字符串，风格为：%Y-%m-%d

    :param date_str:
    :return:
    """

    return parse(date_str, '%Y-%m-%d %H:%M:%S')


def parse(date_str, pattern):
    """
    通过指定的样式来解析日期字符串为日期
    :param date_str: 日期字符串
    :param pattern: 样式
    :return:
    """

    return datetime.datetime.strptime(date_str, pattern)


if __name__ == "__main__":
    print get_now_date_str()
    print get_date_str_before(7)
