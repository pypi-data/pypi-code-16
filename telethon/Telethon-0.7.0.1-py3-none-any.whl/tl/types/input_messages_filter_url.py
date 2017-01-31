from telethon.tl.mtproto_request import MTProtoRequest


class InputMessagesFilterUrl(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    inputMessagesFilterUrl#7ef0dd87  = MessagesFilter"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x7ef0dd87

    def __init__(self):
        super().__init__()

    def on_send(self, writer):
        writer.write_int(InputMessagesFilterUrl.constructor_id, signed=False)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return InputMessagesFilterUrl()

    def on_response(self, reader):
        pass

    def __repr__(self):
        return 'inputMessagesFilterUrl#7ef0dd87  = MessagesFilter'

    def __str__(self):
        return '(inputMessagesFilterUrl (ID: 0x7ef0dd87) = ())'.format()
