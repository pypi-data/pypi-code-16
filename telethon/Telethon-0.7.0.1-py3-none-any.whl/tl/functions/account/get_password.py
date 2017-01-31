from telethon.tl.mtproto_request import MTProtoRequest


class GetPasswordRequest(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    account.getPassword#548a30f5  = account.Password"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x548a30f5

    def __init__(self):
        super().__init__()
        self.result = None
        self.confirmed = True  # Confirmed by default

    def on_send(self, writer):
        writer.write_int(GetPasswordRequest.constructor_id, signed=False)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return GetPasswordRequest()

    def on_response(self, reader):
        self.result = reader.tgread_object()

    def __repr__(self):
        return 'account.getPassword#548a30f5  = account.Password'

    def __str__(self):
        return '(account.getPassword (ID: 0x548a30f5) = ())'.format()
