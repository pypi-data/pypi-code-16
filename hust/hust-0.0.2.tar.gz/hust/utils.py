# -*- coding: utf-8 -*-
'''
Created on Mar 13, 2017

@author: hustcc
'''
from __future__ import absolute_import
from hust import temp


block_comment = {
    'python': '\'\'\'{code}\'\'\'',
    'javascript': '/**{code}**/',
    'java': '/**{code}**/',
    'html': '<!--{code}-->',
    'css': '/**{code}**/',
}


def ascii_string(type, lang='python'):
    try:
        return add_lang_code_comment(getattr(temp, type), lang)
    except:
        return False


# 修改注释的标签
def add_lang_code_comment(code, lang):
    code = '\n{code}\n'.format(code=code)
    return block_comment.get(lang, '/**{code}**/').format(code=code)


if __name__ == '__main__':
    print(ascii_string('girl', 'python'))
