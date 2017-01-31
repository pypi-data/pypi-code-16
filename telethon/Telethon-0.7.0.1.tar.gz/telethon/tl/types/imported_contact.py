from telethon.tl.mtproto_request import MTProtoRequest


class ImportedContact(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    importedContact#d0028438 user_id:int client_id:long = ImportedContact"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xd0028438

    def __init__(self, user_id, client_id):
        """
        :param user_id: Telegram type: «int».
        :param client_id: Telegram type: «long».
        """
        super().__init__()

        self.user_id = user_id
        self.client_id = client_id

    def on_send(self, writer):
        writer.write_int(ImportedContact.constructor_id, signed=False)
        writer.write_int(self.user_id)
        writer.write_long(self.client_id)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return ImportedContact(None, None)

    def on_response(self, reader):
        self.user_id = reader.read_int()
        self.client_id = reader.read_long()

    def __repr__(self):
        return 'importedContact#d0028438 user_id:int client_id:long = ImportedContact'

    def __str__(self):
        return '(importedContact (ID: 0xd0028438) = (user_id={}, client_id={}))'.format(str(self.user_id), str(self.client_id))
