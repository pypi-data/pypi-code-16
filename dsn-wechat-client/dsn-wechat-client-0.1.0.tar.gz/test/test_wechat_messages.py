import unittest
import logging.config

from dsn_wechat.messages import XmlMessage
from dsn_wechat.messages import TextXmlMessage

TEXT_MSG = \
    '<xml>\
        <ToUserName><![CDATA[toUser]]></ToUserName>\
        <FromUserName><![CDATA[fromUser]]></FromUserName>\
        <CreateTime>12345678</CreateTime>\
        <MsgType><![CDATA[text]]></MsgType>\
        <Content><![CDATA[你好]]></Content>\
    </xml>'.encode('UTF-8')


class WechatMessageTestCase(unittest.TestCase):
    def setUp(self):
        logging.config.fileConfig('logging-debug.ini')

    def test_text(self):
        try:
            msg = XmlMessage.decode(TEXT_MSG)
            tm = TextXmlMessage()
            tm.from_user = msg.to_user
            tm.to_user = msg.from_user
            tm.create_time = msg.create_time
            tm.content = msg.content
            print(tm.encode())
        except Exception as e:
            print(e)
            self.fail()
