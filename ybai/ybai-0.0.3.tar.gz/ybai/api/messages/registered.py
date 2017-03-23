#!usr/bin/env python3
# coding:utf-8

from .message import SYSTEM

class Registered(list):
    def __init__(self, bot):
        """
        保存当前机器人所有已注册的消息配置

        :param bot: 所属的机器人
        """
        super(Registered, self).__init__()
        self.bot = bot

    def getConfig(self, msg):
        for conf in self[::-1]:
            return conf
        pass

    def get_config(self, msg):
        """
        获取给定消息的注册配置。每条消息仅匹配一个注册配置，后注册的配置具有更高的匹配优先级。

        :param msg: 给定的消息
        :return: 匹配的回复配置
        """

        for conf in self[::-1]:

            if not conf.enabled or (conf.except_self and msg.sender == self.bot.self):
                continue

            if conf.msg_types and msg.type not in conf.msg_types:
                continue
            elif conf.msg_types is None and msg.type == SYSTEM:
                continue

            if conf.chats is None:
                return conf

            for chat in conf.chats:
                if (isinstance(chat, type) and isinstance(msg.chat, chat)) or chat == msg.chat:
                    return conf