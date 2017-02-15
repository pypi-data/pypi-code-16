#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Filter(logname)，只允许来自logname或其子日志的消息通过app.net是app的子日志
消息传播propagate和分层记录器：消息会传播给父记录器，log.propagate属性获取是否传播标志
在Python中正确的记录Log方式应该是这样的：
    logging.exception(ex)
    logging.error(ex, exc_info=1) # 指名输出栈踪迹, logging.exception的内部也是包了一层此做法
    logging.critical(ex, exc_info=1) # 更加严重的错误级别
"""
import logging
import logging.handlers as handlers
import logging.config as config

# 时间 | 日志级别 | 文件名 | 行号 | 进程ID | Logger名 | 消息体
_fmt = "%(asctime)-15s [%(levelname)s] %(filename)s line=%(lineno)d" \
      " pid=%(process)d %(name)s ===> %(message)s"
_datefmt = "%Y-%m-%d %H:%M:%S"
_formatter = logging.Formatter(_fmt, _datefmt)
_log_dict = {
    'default': '/var/log/default.log',
    'winstore.db': '/var/log/db.log',
}


def _get_key(module_name):
    """根据模块名获取日志key"""
    mlist = module_name.split('.')
    mlen = len(mlist)
    while mlen > 1:
        cutkey = '.'.join(mlist[:mlen])
        if cutkey in _log_dict:
            return cutkey
        mlen -= 1
    return "default"


def get_log(name, level=logging.DEBUG):
    logfile = _log_dict[_get_key(name)]
    _log = logging.getLogger(name)
    _log.propagate = False  # 关闭传播属性
    _log.setLevel(level)
    # 7天轮换一次日志文件
    _handler = logging.handlers.TimedRotatingFileHandler(logfile, when='D', interval=7)
    _handler.setFormatter(_formatter)
    _log.addHandler(_handler)
    return _log

if __name__ == '__main__':
    """main test"""
    _log = get_log(__name__)
    _log.info('this is main.')
    pass
