from telethon.tl.mtproto_request import MTProtoRequest


class GetPeerSettingsRequest(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    messages.getPeerSettings#3672e09c peer:InputPeer = PeerSettings"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x3672e09c

    def __init__(self, peer):
        """
        :param peer: Telegram type: «InputPeer».
        """
        super().__init__()
        self.result = None
        self.confirmed = True  # Confirmed by default

        self.peer = peer

    def on_send(self, writer):
        writer.write_int(GetPeerSettingsRequest.constructor_id, signed=False)
        self.peer.on_send(writer)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return GetPeerSettingsRequest(None)

    def on_response(self, reader):
        self.result = reader.tgread_object()

    def __repr__(self):
        return 'messages.getPeerSettings#3672e09c peer:InputPeer = PeerSettings'

    def __str__(self):
        return '(messages.getPeerSettings (ID: 0x3672e09c) = (peer={}))'.format(str(self.peer))
