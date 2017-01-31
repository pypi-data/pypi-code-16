from telethon.tl.mtproto_request import MTProtoRequest


class InputMessagesFilterVoice(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    inputMessagesFilterVoice#50f5c392  = MessagesFilter"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x50f5c392

    def __init__(self):
        super().__init__()

    def on_send(self, writer):
        writer.write_int(InputMessagesFilterVoice.constructor_id, signed=False)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return InputMessagesFilterVoice()

    def on_response(self, reader):
        pass

    def __repr__(self):
        return 'inputMessagesFilterVoice#50f5c392  = MessagesFilter'

    def __str__(self):
        return '(inputMessagesFilterVoice (ID: 0x50f5c392) = ())'.format()
