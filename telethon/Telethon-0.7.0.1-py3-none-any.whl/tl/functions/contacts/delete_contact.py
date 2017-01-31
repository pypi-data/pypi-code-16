from telethon.tl.mtproto_request import MTProtoRequest


class DeleteContactRequest(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    contacts.deleteContact#8e953744 id:InputUser = contacts.Link"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x8e953744

    def __init__(self, id):
        """
        :param id: Telegram type: «InputUser».
        """
        super().__init__()
        self.result = None
        self.confirmed = True  # Confirmed by default

        self.id = id

    def on_send(self, writer):
        writer.write_int(DeleteContactRequest.constructor_id, signed=False)
        self.id.on_send(writer)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return DeleteContactRequest(None)

    def on_response(self, reader):
        self.result = reader.tgread_object()

    def __repr__(self):
        return 'contacts.deleteContact#8e953744 id:InputUser = contacts.Link'

    def __str__(self):
        return '(contacts.deleteContact (ID: 0x8e953744) = (id={}))'.format(str(self.id))
