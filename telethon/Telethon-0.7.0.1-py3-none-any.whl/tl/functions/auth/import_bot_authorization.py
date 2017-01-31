from telethon.tl.mtproto_request import MTProtoRequest


class ImportBotAuthorizationRequest(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    auth.importBotAuthorization#67a3ff2c flags:int api_id:int api_hash:string bot_auth_token:string = auth.Authorization"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x67a3ff2c

    def __init__(self, flags, api_id, api_hash, bot_auth_token):
        """
        :param flags: Telegram type: «int».
        :param api_id: Telegram type: «int».
        :param api_hash: Telegram type: «string».
        :param bot_auth_token: Telegram type: «string».
        """
        super().__init__()
        self.result = None
        self.confirmed = True  # Confirmed by default

        self.flags = flags
        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_auth_token = bot_auth_token

    def on_send(self, writer):
        writer.write_int(ImportBotAuthorizationRequest.constructor_id, signed=False)
        writer.write_int(self.flags)
        writer.write_int(self.api_id)
        writer.tgwrite_string(self.api_hash)
        writer.tgwrite_string(self.bot_auth_token)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return ImportBotAuthorizationRequest(None, None, None, None)

    def on_response(self, reader):
        self.result = reader.tgread_object()

    def __repr__(self):
        return 'auth.importBotAuthorization#67a3ff2c flags:int api_id:int api_hash:string bot_auth_token:string = auth.Authorization'

    def __str__(self):
        return '(auth.importBotAuthorization (ID: 0x67a3ff2c) = (flags={}, api_id={}, api_hash={}, bot_auth_token={}))'.format(str(self.flags), str(self.api_id), str(self.api_hash), str(self.bot_auth_token))
