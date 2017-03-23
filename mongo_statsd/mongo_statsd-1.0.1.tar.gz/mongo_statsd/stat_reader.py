# -*- coding: utf-8 -*-

import os
import re


class StatReader(object):

    cmd = None
    keys = None

    def __init__(self, cmd, keys):
        """
        :param cmd: 统计命令
        :param keys: 统计命令
        :return:
        """
        self.cmd = cmd
        self.keys = keys

    def read(self):
        """
        读取一次
        :return:
        """

        line = list(os.popen(self.cmd))[0]
        values = re.split(r'\s+', line)

        result = dict(zip(self.keys, values))

        return result
