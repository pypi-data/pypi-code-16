# 与时间相关的模块，如带当前时间的打印方法、格式化时间间隔字符串等
#
# Author: Lex.Teng
# E-mail: lexteng@163.com
# ==============================================================================
import datetime

format_date = '%y-%m-%d'
format_time = '%H:%M:%S'
format_datetime = '%y-%m-%d %H:%M:%S'


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


def get_duration(start, end=None, is_format=True):
    """
    获取时间间隔，默认对时间间隔进行字符串格式化
    时间间隔字符串格式：[hours] h [minutes] min [seconds].[ms] sec

    :param start: 起始时间
    :param end: 结束时间（缺省时使用当前时间）
    :param is_format: 是否对时间间隔进行字符串格式化
    :return: 格式化的时间间隔字符串或毫秒为单位的间隔时间

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

    if is_format:
        if hour > 0:
            return '{} h {:02d} min {:02d}.{:03d} sec'.format(hour, minute, sec, ms)
        elif minute > 0:
            return '{} min {:02d}.{:03d} sec'.format(minute, sec, ms)
        else:
            return '{}.{:03d} sec'.format(sec, ms)
    else:
        return hour*3600000 + minute*60000 + sec*1000 + ms

time_stack = [[], []]


def push_timer(name):
    """
    在时间栈中压入一个计时器
    搜索时间栈需要一定的时间，不建议使用过多的计时器

    :param name: 计时器的名称

    :since: 0.4.1
    """
    time_stack[0].append(name)
    time_stack[1].append(datetime.datetime.now())


def pop_timer(name, is_format=False):
    """
    从时间栈中弹出一个计时器

    :param name: 计时器的名称
    :param is_format: 是否对时间间隔进行字符串格式化
    :return: 格式化的计时时间

    :since: 0.4.1
    """
    index = time_stack[0].index(name)
    ret = get_duration(time_stack[1][index], is_format=is_format)
    time_stack[0].pop(index)
    time_stack[1].pop(index)
    return ret


def read_timer(name, is_format=False):
    """
    读取计时器的当前计时

    :param name: 计时器的名称
    :param is_format: 是否对时间间隔进行字符串格式化
    :return: 格式化的计时时间

    :since: 0.4.1
    """
    index = time_stack[0].index(name)
    return get_duration(time_stack[1][index], is_format=is_format)
