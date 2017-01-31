from telethon.tl.mtproto_request import MTProtoRequest


class GetInlineGameHighScoresRequest(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    messages.getInlineGameHighScores#0f635e1b id:InputBotInlineMessageID user_id:InputUser = messages.HighScores"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xf635e1b

    def __init__(self, id, user_id):
        """
        :param id: Telegram type: «InputBotInlineMessageID».
        :param user_id: Telegram type: «InputUser».
        """
        super().__init__()
        self.result = None
        self.confirmed = True  # Confirmed by default

        self.id = id
        self.user_id = user_id

    def on_send(self, writer):
        writer.write_int(GetInlineGameHighScoresRequest.constructor_id, signed=False)
        self.id.on_send(writer)
        self.user_id.on_send(writer)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return GetInlineGameHighScoresRequest(None, None)

    def on_response(self, reader):
        self.result = reader.tgread_object()

    def __repr__(self):
        return 'messages.getInlineGameHighScores#0f635e1b id:InputBotInlineMessageID user_id:InputUser = messages.HighScores'

    def __str__(self):
        return '(messages.getInlineGameHighScores (ID: 0xf635e1b) = (id={}, user_id={}))'.format(str(self.id), str(self.user_id))
