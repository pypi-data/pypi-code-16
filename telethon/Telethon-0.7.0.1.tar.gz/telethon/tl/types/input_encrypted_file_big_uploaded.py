from telethon.tl.mtproto_request import MTProtoRequest


class InputEncryptedFileBigUploaded(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    inputEncryptedFileBigUploaded#2dc173c8 id:long parts:int key_fingerprint:int = InputEncryptedFile"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x2dc173c8

    def __init__(self, id, parts, key_fingerprint):
        """
        :param id: Telegram type: «long».
        :param parts: Telegram type: «int».
        :param key_fingerprint: Telegram type: «int».
        """
        super().__init__()

        self.id = id
        self.parts = parts
        self.key_fingerprint = key_fingerprint

    def on_send(self, writer):
        writer.write_int(InputEncryptedFileBigUploaded.constructor_id, signed=False)
        writer.write_long(self.id)
        writer.write_int(self.parts)
        writer.write_int(self.key_fingerprint)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return InputEncryptedFileBigUploaded(None, None, None)

    def on_response(self, reader):
        self.id = reader.read_long()
        self.parts = reader.read_int()
        self.key_fingerprint = reader.read_int()

    def __repr__(self):
        return 'inputEncryptedFileBigUploaded#2dc173c8 id:long parts:int key_fingerprint:int = InputEncryptedFile'

    def __str__(self):
        return '(inputEncryptedFileBigUploaded (ID: 0x2dc173c8) = (id={}, parts={}, key_fingerprint={}))'.format(str(self.id), str(self.parts), str(self.key_fingerprint))
