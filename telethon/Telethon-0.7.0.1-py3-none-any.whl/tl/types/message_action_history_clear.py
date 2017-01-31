from telethon.tl.mtproto_request import MTProtoRequest


class MessageActionHistoryClear(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    messageActionHistoryClear#9fbab604  = MessageAction"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x9fbab604

    def __init__(self):
        super().__init__()

    def on_send(self, writer):
        writer.write_int(MessageActionHistoryClear.constructor_id, signed=False)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return MessageActionHistoryClear()

    def on_response(self, reader):
        pass

    def __repr__(self):
        return 'messageActionHistoryClear#9fbab604  = MessageAction'

    def __str__(self):
        return '(messageActionHistoryClear (ID: 0x9fbab604) = ())'.format()
