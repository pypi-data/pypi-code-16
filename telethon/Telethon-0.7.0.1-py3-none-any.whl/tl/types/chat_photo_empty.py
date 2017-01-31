from telethon.tl.mtproto_request import MTProtoRequest


class ChatPhotoEmpty(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    chatPhotoEmpty#37c1011c  = ChatPhoto"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x37c1011c

    def __init__(self):
        super().__init__()

    def on_send(self, writer):
        writer.write_int(ChatPhotoEmpty.constructor_id, signed=False)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return ChatPhotoEmpty()

    def on_response(self, reader):
        pass

    def __repr__(self):
        return 'chatPhotoEmpty#37c1011c  = ChatPhoto'

    def __str__(self):
        return '(chatPhotoEmpty (ID: 0x37c1011c) = ())'.format()
