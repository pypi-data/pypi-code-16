from telethon.tl.mtproto_request import MTProtoRequest


class TopPeerCategoryBotsPM(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    topPeerCategoryBotsPM#ab661b5b  = TopPeerCategory"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xab661b5b

    def __init__(self):
        super().__init__()

    def on_send(self, writer):
        writer.write_int(TopPeerCategoryBotsPM.constructor_id, signed=False)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return TopPeerCategoryBotsPM()

    def on_response(self, reader):
        pass

    def __repr__(self):
        return 'topPeerCategoryBotsPM#ab661b5b  = TopPeerCategory'

    def __str__(self):
        return '(topPeerCategoryBotsPM (ID: 0xab661b5b) = ())'.format()
