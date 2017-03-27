# coding:utf8

"""任务层模块"""

from accesspoint import celeryTask
from fastweb.web import SyncComponents


class CeleryTask(celeryTask, SyncComponents):
    """Celery Task基类

    类成员变量name为任务名称
    run方法为接受参数并运行的函数
    on_success方法为成功回调函数
    on_failure方法为异常回调函数
    on_retry方法为重试回调函数
    """

    # TODO:任务类，定时任务类，异步任务类，同步任务类
    pass
