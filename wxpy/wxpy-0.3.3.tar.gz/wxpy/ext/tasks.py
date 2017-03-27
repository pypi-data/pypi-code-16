import threading


class Tasks(object):
    def __init__(self):
        self.configs = list()

    def __getattr__(self, item):
        if item in ('__iter__', '__getitem__', '__len__', '__contains__'):
            return getattr(self.configs, item)
        return getattr(self, item)

    def incoming(self, n=20):
        """
        用于查看即将执行的 n 个任务

        :param n: 即将执行的任务个数 n
        :return: 即将执行的 n 个任务
        """

        tasks = list()
        rounds = {config: 0 for config in self.configs}

        pass


class BaseTask(object):
    def __init__(self, func, args=None, kwargs=None):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.thread = None
        self.enabled = True

    def run(self):
        self.thread = threading.Thread(
            target=self.func, args=self.args,
            kwargs=self.kwargs, daemon=True
        )

        self.thread.start()

    @property
    def is_alive(self):
        if isinstance(self.thread, threading.Thread):
            return self.thread.is_alive()

    def join(self):
        if self.is_alive:
            self.thread.join()

    def next_datetime(self, n=1):
        """
        | 返回接下来的第 n 次执行的时间点 (datetime.datetime)
        | 由子类实现
        
        :param n: 接下来的第 n 次执行的次数
        """
        raise NotImplementedError

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False


class TimerTask(BaseTask):
    def __init__(
            self, func, secs, minutes=None, hours=None,
            repeat=False, args=None, kwargs=None
    ):
        """
        添加定时任务 (例如: n 秒后执行)

        :param func: 待执行的函数
        :param secs: 间隔的秒数
        :param minutes: 间隔的分钟数
        :param hours: 间隔的小时数
        :param repeat: 是否重复执行
        :param args: 位置参数
        :param kwargs: 命名参数
        """

        super(TimerTask, self).__init__(func=func, args=args, kwargs=kwargs)

        self.secs = secs
        self.minutes = minutes
        self.hours = hours
        self.repeat = repeat

    def next_datetime(self, n=1):
        pass


class PeriodTask(BaseTask):
    def __init__(
            self, func,
            minute=None, hour=None, day=None, mount=None, weekly=None,
            args=None, kwargs=None
    ):
        """
        添加周期性任务 (例如: 每日 9:00 执行)

        :param func: 待执行的函数
        :param minute: 分钟
        :param hour: 小时
        :param day: 日
        :param mount: 月
        :param weekly: 每周 (周日 0~6 周六)
        :param args: 位置参数
        :param kwargs: 命名参数
        """

        super(PeriodTask, self).__init__(func=func, args=args, kwargs=kwargs)

        self.minute = minute
        self.hour = hour
        self.day = day
        self.mount = mount
        self.weekly = weekly

    def next_datetime(self, n=1):
        pass


class DatetimeTask(BaseTask):
    def __init__(self, func, datetime, args=None, kwargs=None):
        """
        添加指定日期时间的任务 (例如: 2017-4-1 9:30:00 执行)
        :param func: 待执行的函数
        :param datetime:
            指定的日期时间，支持以下类型的值:
                * 字符串: 例如 '2017-4-1 9:30:00'
                    * 格式为 '年份-月份-日期 时:分:秒'
                    * 除年份必须为 4 位数外，其他均可为 1 或 2 位数字
                    * 日期为必填部分，末尾的 '时:分:秒' 可部分或完全省略
                * datetime 时间戳: 例如 datetime.datetime(2017, 4, 1, 9, 30, 0)
        :param args: 位置参数
        :param kwargs: 命名参数
        """

        super(DatetimeTask, self).__init__(func=func, args=args, kwargs=kwargs)

        if isinstance(datetime, str):
            pass
        else:
            self.datetime = datetime

    def next_datetime(self, n=1):
        pass
