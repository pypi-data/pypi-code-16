from telethon.tl.mtproto_request import MTProtoRequest


class InputAppEvent(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    inputAppEvent#770656a8 time:double type:string peer:long data:string = InputAppEvent"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x770656a8

    def __init__(self, time, type, peer, data):
        """
        :param time: Telegram type: «double».
        :param type: Telegram type: «string».
        :param peer: Telegram type: «long».
        :param data: Telegram type: «string».
        """
        super().__init__()

        self.time = time
        self.type = type
        self.peer = peer
        self.data = data

    def on_send(self, writer):
        writer.write_int(InputAppEvent.constructor_id, signed=False)
        writer.write_double(self.time)
        writer.tgwrite_string(self.type)
        writer.write_long(self.peer)
        writer.tgwrite_string(self.data)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return InputAppEvent(None, None, None, None)

    def on_response(self, reader):
        self.time = reader.read_double()
        self.type = reader.tgread_string()
        self.peer = reader.read_long()
        self.data = reader.tgread_string()

    def __repr__(self):
        return 'inputAppEvent#770656a8 time:double type:string peer:long data:string = InputAppEvent'

    def __str__(self):
        return '(inputAppEvent (ID: 0x770656a8) = (time={}, type={}, peer={}, data={}))'.format(str(self.time), str(self.type), str(self.peer), str(self.data))
