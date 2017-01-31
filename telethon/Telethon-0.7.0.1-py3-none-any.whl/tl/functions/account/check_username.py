from telethon.tl.mtproto_request import MTProtoRequest


class CheckUsernameRequest(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    account.checkUsername#2714d86c username:string = Bool"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x2714d86c

    def __init__(self, username):
        """
        :param username: Telegram type: «string».
        """
        super().__init__()
        self.result = None
        self.confirmed = True  # Confirmed by default

        self.username = username

    def on_send(self, writer):
        writer.write_int(CheckUsernameRequest.constructor_id, signed=False)
        writer.tgwrite_string(self.username)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return CheckUsernameRequest(None)

    def on_response(self, reader):
        self.result = reader.tgread_object()

    def __repr__(self):
        return 'account.checkUsername#2714d86c username:string = Bool'

    def __str__(self):
        return '(account.checkUsername (ID: 0x2714d86c) = (username={}))'.format(str(self.username))
