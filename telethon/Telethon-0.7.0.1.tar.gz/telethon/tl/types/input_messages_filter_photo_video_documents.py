from telethon.tl.mtproto_request import MTProtoRequest


class InputMessagesFilterPhotoVideoDocuments(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    inputMessagesFilterPhotoVideoDocuments#d95e73bb  = MessagesFilter"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xd95e73bb

    def __init__(self):
        super().__init__()

    def on_send(self, writer):
        writer.write_int(InputMessagesFilterPhotoVideoDocuments.constructor_id, signed=False)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return InputMessagesFilterPhotoVideoDocuments()

    def on_response(self, reader):
        pass

    def __repr__(self):
        return 'inputMessagesFilterPhotoVideoDocuments#d95e73bb  = MessagesFilter'

    def __str__(self):
        return '(inputMessagesFilterPhotoVideoDocuments (ID: 0xd95e73bb) = ())'.format()
