from telethon.tl.mtproto_request import MTProtoRequest


class GetTermsOfServiceRequest(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    help.getTermsOfService#350170f3  = help.TermsOfService"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x350170f3

    def __init__(self):
        super().__init__()
        self.result = None
        self.confirmed = True  # Confirmed by default

    def on_send(self, writer):
        writer.write_int(GetTermsOfServiceRequest.constructor_id, signed=False)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return GetTermsOfServiceRequest()

    def on_response(self, reader):
        self.result = reader.tgread_object()

    def __repr__(self):
        return 'help.getTermsOfService#350170f3  = help.TermsOfService'

    def __str__(self):
        return '(help.getTermsOfService (ID: 0x350170f3) = ())'.format()
