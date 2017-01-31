from telethon.tl.mtproto_request import MTProtoRequest


class GetStatusesRequest(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    contacts.getStatuses#c4a353ee  = Vector<ContactStatus>"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xc4a353ee

    def __init__(self):
        super().__init__()
        self.result = None
        self.confirmed = True  # Confirmed by default

    def on_send(self, writer):
        writer.write_int(GetStatusesRequest.constructor_id, signed=False)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return GetStatusesRequest()

    def on_response(self, reader):
        self.result = reader.tgread_object()

    def __repr__(self):
        return 'contacts.getStatuses#c4a353ee  = Vector<ContactStatus>'

    def __str__(self):
        return '(contacts.getStatuses (ID: 0xc4a353ee) = ())'.format()
