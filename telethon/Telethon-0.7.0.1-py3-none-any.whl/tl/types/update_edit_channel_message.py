from telethon.tl.mtproto_request import MTProtoRequest


class UpdateEditChannelMessage(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    updateEditChannelMessage#1b3f4df7 message:Message pts:int pts_count:int = Update"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x1b3f4df7

    def __init__(self, message, pts, pts_count):
        """
        :param message: Telegram type: «Message».
        :param pts: Telegram type: «int».
        :param pts_count: Telegram type: «int».
        """
        super().__init__()

        self.message = message
        self.pts = pts
        self.pts_count = pts_count

    def on_send(self, writer):
        writer.write_int(UpdateEditChannelMessage.constructor_id, signed=False)
        self.message.on_send(writer)
        writer.write_int(self.pts)
        writer.write_int(self.pts_count)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return UpdateEditChannelMessage(None, None, None)

    def on_response(self, reader):
        self.message = reader.tgread_object()
        self.pts = reader.read_int()
        self.pts_count = reader.read_int()

    def __repr__(self):
        return 'updateEditChannelMessage#1b3f4df7 message:Message pts:int pts_count:int = Update'

    def __str__(self):
        return '(updateEditChannelMessage (ID: 0x1b3f4df7) = (message={}, pts={}, pts_count={}))'.format(str(self.message), str(self.pts), str(self.pts_count))
