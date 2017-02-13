#coding=utf8
import time, logging, mimetypes

import itchatmp
from itchatmp.content import (TEXT, MUSIC,
    IMAGE, VOICE, VIDEO, THUMB, NEWS, CARD)

itchatmp.update_config(itchatmp.WechatConfig(
    token='5tHMP2cZ6UOlscfqyUCuBr',
    appId = 'wx656b8e907615d60c',
    appSecret = 'd4624c36b6795d1d99dcf0547af5443d'))
itchatmp.update_config(filterRequest=True)

itchatmp.set_logging(loggingLevel=logging.DEBUG)

# userList = ['o5Bt8wSaeWlLjnGGwiwRJLS9_pvc', 'o5Bt8weoRUTxjpr_YDA1SX2JhMVA']
# r = itchatmp.menu.get(agentId=5)
# print(r)

@itchatmp.msg_register(itchatmp.content.TEXT)
def text_reply(msg):
    print(msg)
    return msg
    # return {'msgType': itchatmp.content.TEXT, 'content': msg['content']}
    # return '@img@' + msg['mediaId']

itchatmp.run(debug=True)
