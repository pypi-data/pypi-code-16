from telethon.tl.mtproto_request import MTProtoRequest


class GetSupportRequest(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    help.getSupport#9cdf08cd  = help.Support"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x9cdf08cd

    def __init__(self):
        super().__init__()
        self.result = None
        self.confirmed = True  # Confirmed by default

    def on_send(self, writer):
        writer.write_int(GetSupportRequest.constructor_id, signed=False)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return GetSupportRequest()

    def on_response(self, reader):
        self.result = reader.tgread_object()

    def __repr__(self):
        return 'help.getSupport#9cdf08cd  = help.Support'

    def __str__(self):
        return '(help.getSupport (ID: 0x9cdf08cd) = ())'.format()
