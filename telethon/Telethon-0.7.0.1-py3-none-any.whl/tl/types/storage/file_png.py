from telethon.tl.mtproto_request import MTProtoRequest


class FilePng(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    storage.filePng#0a4f63c0  = storage.FileType"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xa4f63c0

    def __init__(self):
        super().__init__()

    def on_send(self, writer):
        writer.write_int(FilePng.constructor_id, signed=False)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return FilePng()

    def on_response(self, reader):
        pass

    def __repr__(self):
        return 'storage.filePng#0a4f63c0  = storage.FileType'

    def __str__(self):
        return '(storage.filePng (ID: 0xa4f63c0) = ())'.format()
