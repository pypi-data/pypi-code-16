# coding:utf8
import re
import types


def num_to_capital_letter(num):
    """ 将数字转为大写字母 wjl

    :param num:
    :return:
    """

    return chr(num + 64)


def letter_to_num(letter):
    """将字母转为数字，无论大小写 wjl

    :param letter:
    :return:
    """

    if isinstance(letter, types.IntType):
        return letter

    import logging
    logging.info(letter)

    return ord(letter.upper()) - 64


def convert_zh_to_spell(str_input):
    """
    取汉字字符串的首字母
    :param str_input: 汉字字符串
    :return: 首字母字符串，大写
    """

    if isinstance(str_input, unicode):
        unicode_str = str_input
    else:
        try:
            unicode_str = str_input.decode('utf8')
        except:
            unicode_str = str_input.decode('gbk')

    return_list = []
    for one_unicode in unicode_str:
        return_list.append(_convert_single_char_to_zh(one_unicode))

    return "".join(return_list).upper()


def _convert_single_char_to_zh(zh_char):
    """
    将单个中文字符转为其拼音首字母
    :param zh_char: 中文字符
    :return: 拼音首字母
    """
    str = zh_char.encode('gbk')

    try:
        ord(str)
        return str
    except:
        asc = ord(str[0]) * 256 + ord(str[1]) - 65536

        if -20319 <= asc <= -20284:
            return 'a'
        if -20283 <= asc <= -19776:
            return 'b'
        if -19775 <= asc <= -19219:
            return 'c'
        if -19218 <= asc <= -18711:
            return 'd'
        if -18710 <= asc <= -18527:
            return 'e'
        if -18526 <= asc <= -18240:
            return 'f'
        if -18239 <= asc <= -17923:
            return 'g'
        if -17922 <= asc <= -17418:
            return 'h'
        if -17417 <= asc <= -16475:
            return 'j'
        if -16474 <= asc <= -16213:
            return 'k'
        if -16212 <= asc <= -15641:
            return 'l'
        if -15640 <= asc <= -15166:
            return 'm'
        if -15165 <= asc <= -14923:
            return 'n'
        if -14922 <= asc <= -14915:
            return 'o'
        if -14914 <= asc <= -14631:
            return 'p'
        if -14630 <= asc <= -14150:
            return 'q'
        if -14149 <= asc <= -14091:
            return 'r'
        if -14090 <= asc <= -13119:
            return 's'
        if -13118 <= asc <= -12839:
            return 't'
        if -12838 <= asc <= -12557:
            return 'w'
        if -12556 <= asc <= -11848:
            return 'x'
        if -11847 <= asc <= -11056:
            return 'y'
        if -11055 <= asc <= -10247:
            return 'z'
        return ''

def string_to_xing(content, frontLen, endLen):
    length = len(content) - frontLen - endLen
    if length < 0:
        return None
    xing = ''
    for i in range(0, length):
        xing = xing + '*'
    a = content[0: frontLen]
    b = content[len(content) - endLen:len(content)]
    return a + xing + b

def isEmoji(comment):
    """
    替换表情
    :param comment:
    :return:
    """
    try:
        # UCS-4
        highpoints = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        # UCS-2
        highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    mytext = highpoints.sub('', comment)
    return mytext


# if __name__ == '__main__':
#     print string_to_xing('15311432059', 3, 0)