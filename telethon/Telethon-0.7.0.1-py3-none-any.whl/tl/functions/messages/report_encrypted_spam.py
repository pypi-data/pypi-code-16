from telethon.tl.mtproto_request import MTProtoRequest


class ReportEncryptedSpamRequest(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    messages.reportEncryptedSpam#4b0c8c0f peer:InputEncryptedChat = Bool"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x4b0c8c0f

    def __init__(self, peer):
        """
        :param peer: Telegram type: «InputEncryptedChat».
        """
        super().__init__()
        self.result = None
        self.confirmed = True  # Confirmed by default

        self.peer = peer

    def on_send(self, writer):
        writer.write_int(ReportEncryptedSpamRequest.constructor_id, signed=False)
        self.peer.on_send(writer)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return ReportEncryptedSpamRequest(None)

    def on_response(self, reader):
        self.result = reader.tgread_object()

    def __repr__(self):
        return 'messages.reportEncryptedSpam#4b0c8c0f peer:InputEncryptedChat = Bool'

    def __str__(self):
        return '(messages.reportEncryptedSpam (ID: 0x4b0c8c0f) = (peer={}))'.format(str(self.peer))
