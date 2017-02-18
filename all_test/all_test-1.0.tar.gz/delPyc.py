#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@contact:    mijiawei@baixing.com
@desc:       删除pyc编译文件
"""
import os


def del_pyc():
    for folder, folders, files in os.walk('.'):
        for filename in files:
            root, ext = os.path.splitext(filename)
            if ext == '.pyc':
                print os.path.abspath(os.path.join(folder, filename))
                os.remove( os.path.abspath(os.path.join(folder, filename ) ) )

if __name__ == "__main__":
    del_pyc()