# coding=utf8

import datetime
import hashlib
from libs.codec_utils import _code


def get_random_filename(files):
    """
    获取一个随机名称

    :param files: 文件
    :return:
    """

    after = ''
    if str(files).__contains__('.'):
        after = '.%s' % (str(files).split('.')[-1])

    now = datetime.datetime.now()
    h = hashlib.md5()
    h.update('%s%s' % (now, _code()))

    return '%s%s' % (h.hexdigest(), after)

