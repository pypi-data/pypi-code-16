# 文件操作模块
#
# Author: Lex.Teng
# E-mail: lexteng@163.com
# ==============================================================================
import numpy as np


def list_to_file(list, path, dtype=">i4"):
    """
    将Python列表（或其他可以直接转为numpy数组的类型）输出为二进制文件

    :param list: 原始列表
    :param path: 输出路径
    :param dtype: 数据格式（默认为">i4"，该格式可以直接被Java的readInt()读取）
    :return: 格式化的当前时间字符串

    :since: 0.4.0
    """
    arr = np.array(list, dtype=dtype)
    arr.tofile(path)
