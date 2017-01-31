from telethon.tl.mtproto_request import MTProtoRequest


class PeerChannel(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    peerChannel#bddde532 channel_id:int = Peer"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xbddde532

    def __init__(self, channel_id):
        """
        :param channel_id: Telegram type: «int».
        """
        super().__init__()

        self.channel_id = channel_id

    def on_send(self, writer):
        writer.write_int(PeerChannel.constructor_id, signed=False)
        writer.write_int(self.channel_id)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return PeerChannel(None)

    def on_response(self, reader):
        self.channel_id = reader.read_int()

    def __repr__(self):
        return 'peerChannel#bddde532 channel_id:int = Peer'

    def __str__(self):
        return '(peerChannel (ID: 0xbddde532) = (channel_id={}))'.format(str(self.channel_id))
