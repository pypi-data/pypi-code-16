#coding=utf8
import time, logging, mimetypes

from tornado import gen, ioloop, concurrent
import itchatmp
from itchatmp.content import (TEXT, MUSIC,
    IMAGE, VOICE, VIDEO, THUMB, NEWS, CARD, SAFE)

itchatmp.update_config(itchatmp.WechatConfig(
    # appId='wx64e7d7261028689d',
    # appSecret='099e4f671158588bb2e6aa39d7590401',
    appId='wx656b8e907615d60c',
    appSecret='d4624c36b6795d1d99dcf0547af5443d',
    token='5tHMP2cZ6UOlscfqyUCuBr',
    encryptMode=SAFE,
    encodingAesKey='WRC6vaDkeIpr2W8TApwKBnIR0UeYmcsTRrcrualfxj5'),)

itchatmp.set_logging(loggingLevel=logging.DEBUG)
logger = logging.getLogger('itchatmp')

@itchatmp.msg_register(itchatmp.content.INCOME_MSG)
def text_reply(msg):
    logger.debug(msg)
    # return msg['Content']
# itchatmp.run()

toUserName = 'o5Bt8weoRUTxjpr_YDA1SX2JhMVA'
# toUserName = 'ohUezszIUcrTEsQaUjMwuXMFGhSw'

# r = itchatmp.customerservice.send(TEXT, 'hi', toUserId=toUserName)
r = itchatmp.send('hi', toUserName)
# r = itchatmp.messages.preview(TEXT, 'hi', toUserId=toUserName)
print(r)
