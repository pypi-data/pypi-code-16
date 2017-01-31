from telethon.tl.mtproto_request import MTProtoRequest


class InputPhoto(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    inputPhoto#fb95c6c4 id:long access_hash:long = InputPhoto"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xfb95c6c4

    def __init__(self, id, access_hash):
        """
        :param id: Telegram type: «long».
        :param access_hash: Telegram type: «long».
        """
        super().__init__()

        self.id = id
        self.access_hash = access_hash

    def on_send(self, writer):
        writer.write_int(InputPhoto.constructor_id, signed=False)
        writer.write_long(self.id)
        writer.write_long(self.access_hash)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return InputPhoto(None, None)

    def on_response(self, reader):
        self.id = reader.read_long()
        self.access_hash = reader.read_long()

    def __repr__(self):
        return 'inputPhoto#fb95c6c4 id:long access_hash:long = InputPhoto'

    def __str__(self):
        return '(inputPhoto (ID: 0xfb95c6c4) = (id={}, access_hash={}))'.format(str(self.id), str(self.access_hash))
