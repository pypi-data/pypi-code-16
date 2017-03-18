# 文件操作模块
#
# Author: Lex.Teng
# E-mail: lexteng@163.com
# ==============================================================================
import numpy as np
import os


def list_to_file(list, path, dtype=">i4", overwrite=True):
    """
    将Python列表（或其他可以直接转为numpy数组的类型）输出为二进制文件

    :param list: 原始列表
    :param path: 输出路径
    :param dtype: 数据格式（默认为">i4"，该格式可以直接被Java的readInt()读取）
    :param overwrite: 是否以覆盖方式写入（为False时表示以追加方式写入）
    :return: 格式化的当前时间字符串

    :since: 0.4.0
    """
    op = 'w'
    arr = np.array(list, dtype=dtype)
    mkdirs(path)
    if not overwrite:
        op = 'a'
    f = open(path, op)
    arr.tofile(f)


def mkdirs(path):
    """
    创建路径所指的文件夹，存在时跳过创建

    :param path: 目标路径
    :return: 创建成功返回True，文件夹已存在时返回False

    :since: 0.4.1
    """
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)
        return True
    return False
