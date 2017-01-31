from telethon.tl.mtproto_request import MTProtoRequest


class InputMediaGame(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    inputMediaGame#d33f43f3 id:InputGame = InputMedia"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xd33f43f3

    def __init__(self, id):
        """
        :param id: Telegram type: «InputGame».
        """
        super().__init__()

        self.id = id

    def on_send(self, writer):
        writer.write_int(InputMediaGame.constructor_id, signed=False)
        self.id.on_send(writer)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return InputMediaGame(None)

    def on_response(self, reader):
        self.id = reader.tgread_object()

    def __repr__(self):
        return 'inputMediaGame#d33f43f3 id:InputGame = InputMedia'

    def __str__(self):
        return '(inputMediaGame (ID: 0xd33f43f3) = (id={}))'.format(str(self.id))
