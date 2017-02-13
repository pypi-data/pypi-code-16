#coding=utf-8

from weixunsdkcore.request import WeixunRequest


class FrsRequest(WeixunRequest):
    """
    Face recognize Service Request
    """
    def __init__(self, function, *args, **kwargs):
        WeixunRequest.__init__(self, 'face', 'v20170213', function, *args, **kwargs)