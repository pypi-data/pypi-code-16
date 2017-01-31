from telethon.tl.mtproto_request import MTProtoRequest


class FilePartial(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    storage.filePartial#40bc6f52  = storage.FileType"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x40bc6f52

    def __init__(self):
        super().__init__()

    def on_send(self, writer):
        writer.write_int(FilePartial.constructor_id, signed=False)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return FilePartial()

    def on_response(self, reader):
        pass

    def __repr__(self):
        return 'storage.filePartial#40bc6f52  = storage.FileType'

    def __str__(self):
        return '(storage.filePartial (ID: 0x40bc6f52) = ())'.format()
