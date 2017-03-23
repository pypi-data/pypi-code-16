class Tasks(object):
    def __init__(self):
        self.tasks = list()

    def add_timer(self, func, secs, args=None, kwargs=None, repeat=False):
        """
        添加定时任务 (n 秒后执行)

        :param func: 待执行的函数
        :param secs: 间隔的秒数
        :param args: 位置参数
        :param kwargs: 命名参数
        :param repeat: 重复执行
        """

        raise NotImplementedError

    def add_period(self, func, minute, hour, day, mount, weekly, args, kwargs):
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

        raise NotImplementedError

    def scheduled(self, next_n=20):
        """
        列出即将执行的 n 个任务

        :param next_n: 个数 n
        :return: 即将执行的 n 个任务
        """

        raise NotImplementedError
