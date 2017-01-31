from telethon.tl.mtproto_request import MTProtoRequest


class TopPeerCategoryBotsInline(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    topPeerCategoryBotsInline#148677e2  = TopPeerCategory"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x148677e2

    def __init__(self):
        super().__init__()

    def on_send(self, writer):
        writer.write_int(TopPeerCategoryBotsInline.constructor_id, signed=False)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return TopPeerCategoryBotsInline()

    def on_response(self, reader):
        pass

    def __repr__(self):
        return 'topPeerCategoryBotsInline#148677e2  = TopPeerCategory'

    def __str__(self):
        return '(topPeerCategoryBotsInline (ID: 0x148677e2) = ())'.format()
