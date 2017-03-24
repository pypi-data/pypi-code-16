# coding=utf8

import hashlib
import random


def _code(number=12):
    code_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
                 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x',
                 'y', 'z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
    return ''.join(c for c in random.sample(code_list, number))

def get_file_md5(f_path):
    """
    获取文件的md5值

    :param f_path: 文件路径
    :return:
    """

    md5file = open(f_path, 'rb')
    rawmd5 = hashlib.md5(md5file.read()).hexdigest()
    md5file.close()
    return rawmd5
