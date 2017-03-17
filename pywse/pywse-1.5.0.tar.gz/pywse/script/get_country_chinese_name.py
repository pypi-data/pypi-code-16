# -*- coding:utf-8 -*-

import requests
import json
from pywse.conf.countries import questions
import time

if __name__ == '__main__':
    url = 'http://fanyi.baidu.com/v2transapi'
    for question in questions:
        data = {'from': 'en','to':'zh','query':question['name'],'transtype':'realtime','simple_means_flag':'3'}
        r = requests.post(url,data=data)
        content = r.content
        content = json.loads(content)
        name_zh = content.get('dict_result', {})
        if name_zh:
            name_zh = name_zh.get('simple_means', {}).get('word_means', ['',])[0]
        else:
            name_zh = content.get('trans_result', {}).get('keywords', [{},])[0].get('means', ['',])[0]
        name_zh = name_zh.replace(u'(1917\u5e74\u4ee5\u524d\u7684)', '')
        slice_first_list = (u'（','[','(',u'，',)
        for slice in slice_first_list:
            if slice in name_zh:
                name_zh = name_zh.split(slice)[0]
        question['name_zh'] = name_zh
        question = str(question)
        question = question.replace("u'", "'")
        exec('question=u"""    %s"""' % (question))
        question =question.replace("'name_zh': ", "'name_zh': u")
        question += ','
        print question
        time.sleep(1)

