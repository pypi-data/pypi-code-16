from telethon.tl.mtproto_request import MTProtoRequest


class ReceivedNotifyMessage(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    receivedNotifyMessage#a384b779 id:int flags:int = ReceivedNotifyMessage"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xa384b779

    def __init__(self, id, flags):
        """
        :param id: Telegram type: «int».
        :param flags: Telegram type: «int».
        """
        super().__init__()

        self.id = id
        self.flags = flags

    def on_send(self, writer):
        writer.write_int(ReceivedNotifyMessage.constructor_id, signed=False)
        writer.write_int(self.id)
        writer.write_int(self.flags)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return ReceivedNotifyMessage(None, None)

    def on_response(self, reader):
        self.id = reader.read_int()
        self.flags = reader.read_int()

    def __repr__(self):
        return 'receivedNotifyMessage#a384b779 id:int flags:int = ReceivedNotifyMessage'

    def __str__(self):
        return '(receivedNotifyMessage (ID: 0xa384b779) = (id={}, flags={}))'.format(str(self.id), str(self.flags))
