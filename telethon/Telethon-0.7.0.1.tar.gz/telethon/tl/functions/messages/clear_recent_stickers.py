from telethon.tl.mtproto_request import MTProtoRequest


class ClearRecentStickersRequest(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    messages.clearRecentStickers#8999602d flags:None attached:flags.0?true = Bool"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x8999602d

    def __init__(self, attached=None):
        """
        :param attached: Telegram type: «true».
        """
        super().__init__()
        self.result = None
        self.confirmed = True  # Confirmed by default

        self.attached = attached

    def on_send(self, writer):
        writer.write_int(ClearRecentStickersRequest.constructor_id, signed=False)
        # Calculate the flags. This equals to those flag arguments which are NOT None
        flags = 0
        flags |= (1 << 0) if self.attached else 0
        writer.write_int(flags)


    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return ClearRecentStickersRequest(None)

    def on_response(self, reader):
        self.result = reader.tgread_object()

    def __repr__(self):
        return 'messages.clearRecentStickers#8999602d flags:None attached:flags.0?true = Bool'

    def __str__(self):
        return '(messages.clearRecentStickers (ID: 0x8999602d) = (attached={}))'.format(str(self.attached))
