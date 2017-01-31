from telethon.tl.mtproto_request import MTProtoRequest


class UpdatesTooLong(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    updatesTooLong#e317af7e  = Updates"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xe317af7e

    def __init__(self):
        super().__init__()

    def on_send(self, writer):
        writer.write_int(UpdatesTooLong.constructor_id, signed=False)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return UpdatesTooLong()

    def on_response(self, reader):
        pass

    def __repr__(self):
        return 'updatesTooLong#e317af7e  = Updates'

    def __str__(self):
        return '(updatesTooLong (ID: 0xe317af7e) = ())'.format()
