from telethon.tl.mtproto_request import MTProtoRequest


class PeerNotifyEventsEmpty(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    peerNotifyEventsEmpty#add53cb3  = PeerNotifyEvents"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xadd53cb3

    def __init__(self):
        super().__init__()

    def on_send(self, writer):
        writer.write_int(PeerNotifyEventsEmpty.constructor_id, signed=False)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return PeerNotifyEventsEmpty()

    def on_response(self, reader):
        pass

    def __repr__(self):
        return 'peerNotifyEventsEmpty#add53cb3  = PeerNotifyEvents'

    def __str__(self):
        return '(peerNotifyEventsEmpty (ID: 0xadd53cb3) = ())'.format()
