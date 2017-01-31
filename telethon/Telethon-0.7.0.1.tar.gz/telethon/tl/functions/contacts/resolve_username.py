from telethon.tl.mtproto_request import MTProtoRequest


class ResolveUsernameRequest(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    contacts.resolveUsername#f93ccba3 username:string = contacts.ResolvedPeer"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xf93ccba3

    def __init__(self, username):
        """
        :param username: Telegram type: «string».
        """
        super().__init__()
        self.result = None
        self.confirmed = True  # Confirmed by default

        self.username = username

    def on_send(self, writer):
        writer.write_int(ResolveUsernameRequest.constructor_id, signed=False)
        writer.tgwrite_string(self.username)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return ResolveUsernameRequest(None)

    def on_response(self, reader):
        self.result = reader.tgread_object()

    def __repr__(self):
        return 'contacts.resolveUsername#f93ccba3 username:string = contacts.ResolvedPeer'

    def __str__(self):
        return '(contacts.resolveUsername (ID: 0xf93ccba3) = (username={}))'.format(str(self.username))
