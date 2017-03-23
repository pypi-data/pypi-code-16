#!usr/bin/env python
# coding:utf-8

# 系统
SYSTEM = 'System'
# 文本
TEXT = 'Text'
# 视频
VIDEO = 'Video'

class Message(object):


    @property
    def chat(self):
        """
        消息所在的聊天会话，即:

            对于自己发送的消息，为消息的接收者；
            对于别人发送的消息，为消息的发送者。
        """
        print('Message--chat()')
        # if self.raw.get('FromUserName') == self.bot.self.user_name:
        #     return self.receiver
        # else:
        #     return self.sender