# -*- coding: utf-8 -*-
import requests
from .compat import basestring


class YunPianError(Exception):
    pass


class YunPian(object):
    """设置项:
    YUNPIAN_APIKEY
    YUNPIAN_CONTENT_PREFIX:  eg. '【小熊快跑】'

    API: https://www.yunpian.com/api2.0/howto.html
    """
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.apikey = app.config['YUNPIAN_APIKEY']
        self.default_sign = app.config['YUNPIAN_DEFAULT_SIGN']

    def send(self, phones, content, sign=None):
        """发送短信

        :params phones: 接收短信的手机号或者手机号列表
        :params conent: 短信内容
        :params sign: 签名， 不包含【】, 如果为None， 则使用配置的默认签名
        :return: 云片服务器返回的json数据
        """
        assert phones

        if isinstance(phones, basestring):
            url = 'https://sms.yunpian.com/v2/sms/single_send.json'
            mobile = phones
        else:
            url = 'https://sms.yunpian.com/v2/sms/batch_send.json'
            mobile = ','.join(phones)

        if sign is None:
            sign = self.default_sign
        text = '【{}】{}'.format(sign, content)

        data = dict(
            apikey=self.apikey,
            mobile=mobile,
            text=text,
        )
        r = requests.post(url, data=data)

        return r.json()
