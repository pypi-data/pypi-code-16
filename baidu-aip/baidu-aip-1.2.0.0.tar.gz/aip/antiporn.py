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

class AipAntiPorn(AipBase):
    """
        Aip antiporn
    """

    __detectUrl = 'https://aip.baidubce.com/rest/2.0/antiporn/v1/detect'
    
    def detect(self, image):
        """
            Aip antiporn check
        """

        data = {}
        data['image'] = image

        return self._request(self.__detectUrl, data)

    def _validate(self, url, data):
        """
            validate
        """

        img = Image.open(StringIO(data['image']))

        format = img.format.upper()
        width, height = img.size

        # 图片格式检查
        if format not in ['JPEG', 'BMP', 'PNG', 'GIF']:
            return {
                'error_code': 'SDK109',
                'error_msg': 'unsupported image format',
            }

        data['image'] = base64.b64encode(data['image'])

        # 编码后小于4m
        if len(data['image']) >= 4 * 1024 * 1024:
            return {
                'error_code': 'SDK100',
                'error_msg': 'image size error',
            }

        return True