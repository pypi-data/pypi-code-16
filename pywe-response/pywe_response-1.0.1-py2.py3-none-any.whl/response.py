# -*- coding: utf-8 -*-

WXPAY_NOTIFY_SUCCESS = '<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>'
WXPAY_NOTIFY_FAIL = '<xml><return_code><![CDATA[FAIL]]></return_code><return_msg><![CDATA[XML PARSE FAIL]]></return_msg></xml>'
# 支付回调频率，通知频率为 15/15/30/180/1800/1800/1800/1800/3600，单位：秒
WXPAY_NOTIFY_RETRY_INTERVAL = [15, 15, 30, 180, 1800, 1800, 1800, 1800, 3600]
