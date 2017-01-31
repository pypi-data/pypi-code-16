from telethon.tl.mtproto_request import MTProtoRequest


class MessageEntityMention(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    messageEntityMention#fa04579d offset:int length:int = MessageEntity"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xfa04579d

    def __init__(self, offset, length):
        """
        :param offset: Telegram type: «int».
        :param length: Telegram type: «int».
        """
        super().__init__()

        self.offset = offset
        self.length = length

    def on_send(self, writer):
        writer.write_int(MessageEntityMention.constructor_id, signed=False)
        writer.write_int(self.offset)
        writer.write_int(self.length)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return MessageEntityMention(None, None)

    def on_response(self, reader):
        self.offset = reader.read_int()
        self.length = reader.read_int()

    def __repr__(self):
        return 'messageEntityMention#fa04579d offset:int length:int = MessageEntity'

    def __str__(self):
        return '(messageEntityMention (ID: 0xfa04579d) = (offset={}, length={}))'.format(str(self.offset), str(self.length))
