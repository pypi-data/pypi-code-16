# -*- coding: utf-8 -*-

import re
import sys
from .base import AipBase
from .base import base64
from .base import json
from .base import urlencode
from .base import quote
from .base import Image
from .base import StringIO

class AipNlp(AipBase):
    """
        Aip NLP
    """

    __wordsegUrl = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/wordseg'
    
    __wordposUrl = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/wordpos'
    
    __wordembeddingUrl = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/wordembedding'
    
    __dnnlmUrl = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/dnnlm_cn'
    
    __simnetUrl = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/simnet'
    
    __commentTagUrl = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/comment_tag'

    def _proccessResult(self, content):
        """
            formate result
        """
        
        if sys.version_info.major == 2:
            return json.loads(content.decode('gbk', 'ignore').encode('utf8')) or {}
        else:
            return json.loads(str(content, 'gbk')) or {}

    def __processData(self, content):
        """
            processData
        """
        
        if sys.version_info.major == 2:
            return json.dumps(content, ensure_ascii=False)
        else:
            return json.dumps(content)

    def __encode(self, s):
        """
            编码
        """

        if sys.version_info.major == 2:
            return quote(s.decode('utf8').encode('gbk'))
        else:
            return quote(s.encode('gbk'))
    
    def wordseg(self, query):
        """
            Aip wordseg
        """

        data = {}
        data['query'] = self.__encode(query)

        return self._request(self.__wordsegUrl, self.__processData(data))

    def wordpos(self, query):
        """
            Aip wordpos
        """

        data = {}
        data['query'] = self.__encode(query)

        return self._request(self.__wordposUrl, self.__processData(data))

    def wordembedding(self, query1, query2=''):
        """
            Aip wordembedding
        """

        data = {}
        data['query1'] = self.__encode(query1)

        if query2:
            data['query2'] = self.__encode(query2)
            data['tid'] = 1
        else:
            data['tid'] = 2

        return self._request(self.__wordembeddingUrl, self.__processData(data))

    def dnnlm(self, query):
        """
            Aip dnnlm
        """

        data = {}
        data['input_sequence'] = self.__encode(query)

        return self._request(self.__dnnlmUrl, self.__processData(data))

    def simnet(self, query1, query2, options=None):
        """
            Aip simnet
        """

        options = options or {}
        data = {}
        data['input'] = {
            'qslots':[{
                'terms_sequence': self.__encode(query1),
                'type': 0,
                'items': [],
            }],
            'tslots':[{
                'terms_sequence': self.__encode(query2),
                'type': 0,
                'items': [],
            }],
            'type': options.get('type', 0),
        }

        return self._request(self.__simnetUrl, self.__processData(data))

    def commentTag(self, comment, options=None):
        """
            Aip commentTag
        """

        options = options or {}
        data = {}
        data['comment'] = self.__encode(comment)
        data['type'] = str(options.get('type', '4'))
        data['entity'] = options.get('entity', 'NULL')

        return self._request(self.__commentTagUrl, self.__processData(data))
