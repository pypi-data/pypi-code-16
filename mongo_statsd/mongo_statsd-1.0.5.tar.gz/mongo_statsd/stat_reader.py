# -*- coding: utf-8 -*-

import os
import re

from . import constants

class StatReader(object):

    cmd = None
    keys = None

    def __init__(self, cmd):
        """
        :param cmd: 统计命令
        :param keys: 统计命令
        :return:
        """
        self.cmd = cmd

    def read(self):
        """
        读取一次
        :return:
        """

        keys = None
        values = None

        for line in os.popen(self.cmd):
            line = line.strip()
            if line.startswith('connected'):
                continue

            if line.startswith('insert'):
                # 将有空格的header替换掉
                for old_header, new_header in constants.REPLACE_HEADER_LIST.items():
                    line = line.replace(old_header, new_header)

                keys = re.split(r'\s+', line)
                continue

            values = re.split(r'\s+', line)
            break

        result = dict(zip(keys, values))

        return result
