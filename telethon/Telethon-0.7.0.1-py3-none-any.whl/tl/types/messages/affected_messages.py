from telethon.tl.mtproto_request import MTProtoRequest


class AffectedMessages(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    messages.affectedMessages#84d19185 pts:int pts_count:int = messages.AffectedMessages"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x84d19185

    def __init__(self, pts, pts_count):
        """
        :param pts: Telegram type: «int».
        :param pts_count: Telegram type: «int».
        """
        super().__init__()

        self.pts = pts
        self.pts_count = pts_count

    def on_send(self, writer):
        writer.write_int(AffectedMessages.constructor_id, signed=False)
        writer.write_int(self.pts)
        writer.write_int(self.pts_count)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return AffectedMessages(None, None)

    def on_response(self, reader):
        self.pts = reader.read_int()
        self.pts_count = reader.read_int()

    def __repr__(self):
        return 'messages.affectedMessages#84d19185 pts:int pts_count:int = messages.AffectedMessages'

    def __str__(self):
        return '(messages.affectedMessages (ID: 0x84d19185) = (pts={}, pts_count={}))'.format(str(self.pts), str(self.pts_count))
