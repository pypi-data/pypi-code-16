from telethon.tl.mtproto_request import MTProtoRequest


class MessageRange(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    messageRange#0ae30253 min_id:int max_id:int = MessageRange"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xae30253

    def __init__(self, min_id, max_id):
        """
        :param min_id: Telegram type: «int».
        :param max_id: Telegram type: «int».
        """
        super().__init__()

        self.min_id = min_id
        self.max_id = max_id

    def on_send(self, writer):
        writer.write_int(MessageRange.constructor_id, signed=False)
        writer.write_int(self.min_id)
        writer.write_int(self.max_id)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return MessageRange(None, None)

    def on_response(self, reader):
        self.min_id = reader.read_int()
        self.max_id = reader.read_int()

    def __repr__(self):
        return 'messageRange#0ae30253 min_id:int max_id:int = MessageRange'

    def __str__(self):
        return '(messageRange (ID: 0xae30253) = (min_id={}, max_id={}))'.format(str(self.min_id), str(self.max_id))
