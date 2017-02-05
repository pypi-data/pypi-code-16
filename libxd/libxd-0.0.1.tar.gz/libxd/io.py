# -*- coding: utf-8 -*-
#
# Created by libxd on 17-2-5.
#
import os


class FileUtils(object):
    """
    这个类用来处理跟文件有关的功能
    """
    @staticmethod
    def file_name(path):
        """
        给出一个文件的路径，返回去掉了扩展名的文件名
        :param path: str, 文件的路径
        :return: str, 去掉了扩展名的文件名
        """
        return os.path.splitext(os.path.basename(path))[0]
