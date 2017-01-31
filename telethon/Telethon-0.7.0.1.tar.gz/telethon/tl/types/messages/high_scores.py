from telethon.tl.mtproto_request import MTProtoRequest


class HighScores(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    messages.highScores#9a3bfd99 scores:Vector<HighScore> users:Vector<User> = messages.HighScores"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x9a3bfd99

    def __init__(self, scores, users):
        """
        :param scores: Telegram type: «HighScore». Must be a list.
        :param users: Telegram type: «User». Must be a list.
        """
        super().__init__()

        self.scores = scores
        self.users = users

    def on_send(self, writer):
        writer.write_int(HighScores.constructor_id, signed=False)
        writer.write_int(0x1cb5c415, signed=False)  # Vector's constructor ID
        writer.write_int(len(self.scores))
        for scores_item in self.scores:
            scores_item.on_send(writer)

        writer.write_int(0x1cb5c415, signed=False)  # Vector's constructor ID
        writer.write_int(len(self.users))
        for users_item in self.users:
            users_item.on_send(writer)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return HighScores(None, None)

    def on_response(self, reader):
        reader.read_int()  # Vector's constructor ID
        self.scores = []  # Initialize an empty list
        scores_len = reader.read_int()
        for _ in range(scores_len):
            scores_item = reader.tgread_object()
            self.scores.append(scores_item)

        reader.read_int()  # Vector's constructor ID
        self.users = []  # Initialize an empty list
        users_len = reader.read_int()
        for _ in range(users_len):
            users_item = reader.tgread_object()
            self.users.append(users_item)

    def __repr__(self):
        return 'messages.highScores#9a3bfd99 scores:Vector<HighScore> users:Vector<User> = messages.HighScores'

    def __str__(self):
        return '(messages.highScores (ID: 0x9a3bfd99) = (scores={}, users={}))'.format(None if not self.scores else [str(_) for _ in self.scores], None if not self.users else [str(_) for _ in self.users])
