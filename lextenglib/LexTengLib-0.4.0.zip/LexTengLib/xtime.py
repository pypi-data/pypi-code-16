# 与时间相关的模块，如带当前时间的打印方法、格式化时间间隔字符串等
#
# Author: Lex.Teng
# E-mail: lexteng@163.com
# ==============================================================================
import datetime


def get_time_str(time=None, time_format='%H:%M:%S'):
    """
    获取格式化的当前时间字符串

    :param time: 指定时间，缺省时为当前时间
    :param time_format: strftime时间格式
    :return: 格式化的当前时间字符串

    :since: 0.2.0
    """
    if not time:
        time = datetime.datetime.now()
    return time.strftime(time_format)


def time_print(message, separator=': ', time_format='%H:%M:%S'):
    """
    打印带有当前时间的信息

    :param message: 打印信息
    :param separator: 时间和信息的分隔符
    :param time_format: strftime时间格式
    :return: None

    :since: 0.2.0
    """
    print(get_time_str(time_format=time_format) + separator + message)


def ms_time_print(message, separator=': '):
    """
    打印带有当前时间的信息，精确到毫秒

    :param message: 打印信息
    :param separator: 时间和信息的分隔符
    :return: None

    :since: 0.2.0
    """
    now = datetime.datetime.now()
    time_str = now.strftime('%H:%M:%S')
    time_str = '{}.{:03d}'.format(time_str, (now.microsecond + 5) // 1000)
    print(time_str + separator + message)


def get_duration(start, end=None):
    """
    获取格式化的时间间隔字符串：[hours] [minutes] seconds.ms

    :param start: 起始时间
    :param end: 结束时间（缺省时使用当前时间）
    :return: 格式化的时间间隔字符串

    :since: 0.2.0
    """
    if not end:
        end = datetime.datetime.now()

    ms = ((end - start).microseconds + 500) // 1000
    during = (end - start).seconds
    sec = during % 60
    during //= 60
    minute = during % 60
    hour = during // 60

    if hour > 0:
        return '{} h {:02d} min {:02d}.{:03d} sec'.format(hour, minute, sec, ms)
    elif minute > 0:
        return '{} min {:02d}.{:03d} sec'.format(minute, sec, ms)
    else:
        return '{}.{:03d} sec'.format(sec, ms)
