from telethon.tl.mtproto_request import MTProtoRequest


class GetStickerSetRequest(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    messages.getStickerSet#2619a90e stickerset:InputStickerSet = messages.StickerSet"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x2619a90e

    def __init__(self, stickerset):
        """
        :param stickerset: Telegram type: «InputStickerSet».
        """
        super().__init__()
        self.result = None
        self.confirmed = True  # Confirmed by default

        self.stickerset = stickerset

    def on_send(self, writer):
        writer.write_int(GetStickerSetRequest.constructor_id, signed=False)
        self.stickerset.on_send(writer)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return GetStickerSetRequest(None)

    def on_response(self, reader):
        self.result = reader.tgread_object()

    def __repr__(self):
        return 'messages.getStickerSet#2619a90e stickerset:InputStickerSet = messages.StickerSet'

    def __str__(self):
        return '(messages.getStickerSet (ID: 0x2619a90e) = (stickerset={}))'.format(str(self.stickerset))
