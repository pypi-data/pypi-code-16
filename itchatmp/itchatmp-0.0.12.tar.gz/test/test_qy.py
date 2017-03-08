import itchatmp
from itchatmp.content import FILE

itchatmp.update_config(itchatmp.WechatConfig(
    token='48fLSTTBDVI5TIDpd1gLdFYwKqex4Mk',
    copId = 'wx34c7eb36575d6084',
    appSecret = 'iWPsYqgLW5OWmhUpIXcSlOjwkWjZyGImSJy20F2d9auXmoO6OpSqPXEixgPfJfW5',
    encryptMode=itchatmp.content.SAFE,
    encodingAesKey='LRHlWAmF8Rhq3wdtmuLj4XTrQVjJVlo8okiCOA9XiTb',))

# @itchatmp.msg_register(itchatmp.content.INCOME_MSG)
# def reply(msg):
#     return '@fil@test.py'
    # return msg['Content']

toUserName = 'LittleCoder'
r = itchatmp.messages.upload(FILE, 'test.py')
if r:
    mediaId = r['media_id']
r = itchatmp.messages.send_some(FILE, mediaId,
    targetIdList=[toUserName], agentId=5)
print(r)

# itchatmp.run()
