import logging
import xml.etree.ElementTree as ETree

"""
封装微信的几种消息结构\
微信也挺神奇，接收到的消息是XML格式，发出的消息确是JSON格式.\
难道不是同一个开发团队？求解

"""


def _get_logger():
    return logging.getLogger('dsn.wechat.messages')


class XmlMessage:
    """基类，封装共性字段和方法"""

    def __init__(self):
        self._xml = {}

    def _initialize(self, data: dict):
        self._xml = data

    @property
    def type(self):
        return self._xml.get('MsgType')

    @property
    def to_user(self):
        return self._xml.get('ToUserName')

    @to_user.setter
    def to_user(self, to_user):
        self._xml['ToUserName'] = to_user

    @property
    def from_user(self):
        return self._xml.get('FromUserName')

    @from_user.setter
    def from_user(self, from_user):
        self._xml['FromUserName'] = from_user

    @property
    def create_time(self):
        return self._xml.get('CreateTime')

    @create_time.setter
    def create_time(self, create_time):
        self._xml['CreateTime'] = create_time

    def encode(self, encoding='UTF-8'):
        logger = _get_logger()
        root = ETree.Element('xml')
        for (k, v) in self._xml.items():
            logger.debug('add <%(tag)s>%(value)s</%(tag)s>'
                         % {'tag': k, 'value': v})
            se = ETree.SubElement(root, k)
            se.text = v
        return ETree.tostring(root, encoding=encoding)

    @classmethod
    def decode(cls, data: bytes, encoding='UTF-8'):
        xml_string = data.decode(encoding)
        # logger.debug('decoding :\n %s', xml_string)
        root = ETree.fromstring(xml_string)
        msg = dict()
        children = list(root)
        for el in children:
            msg[el.tag] = el.text

        msg_type = msg['MsgType']
        if msg_type is None:
            raise KeyError('unknow message type')
        msg_cls = _XML_MSG_MAP[msg_type]
        if not msg_cls:
            raise KeyError('unknow message type:%s', msg_type)
        obj = msg_cls()
        obj._initialize(msg)
        return obj


class TextXmlMessage(XmlMessage):
    """Text类型"""

    @property
    def content(self):
        return self._xml.get('Content')

    @content.setter
    def content(self, content):
        self._xml['Content'] = content


_XML_MSG_MAP = {
    'text': TextXmlMessage
}
