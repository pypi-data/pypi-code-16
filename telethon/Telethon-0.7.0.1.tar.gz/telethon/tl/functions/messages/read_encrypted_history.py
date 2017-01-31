from telethon.tl.mtproto_request import MTProtoRequest


class ReadEncryptedHistoryRequest(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    messages.readEncryptedHistory#7f4b690a peer:InputEncryptedChat max_date:date = Bool"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x7f4b690a

    def __init__(self, peer, max_date):
        """
        :param peer: Telegram type: «InputEncryptedChat».
        :param max_date: Telegram type: «date».
        """
        super().__init__()
        self.result = None
        self.confirmed = True  # Confirmed by default

        self.peer = peer
        self.max_date = max_date

    def on_send(self, writer):
        writer.write_int(ReadEncryptedHistoryRequest.constructor_id, signed=False)
        self.peer.on_send(writer)
        writer.tgwrite_date(self.max_date)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return ReadEncryptedHistoryRequest(None, None)

    def on_response(self, reader):
        self.result = reader.tgread_object()

    def __repr__(self):
        return 'messages.readEncryptedHistory#7f4b690a peer:InputEncryptedChat max_date:date = Bool'

    def __str__(self):
        return '(messages.readEncryptedHistory (ID: 0x7f4b690a) = (peer={}, max_date={}))'.format(str(self.peer), str(self.max_date))
