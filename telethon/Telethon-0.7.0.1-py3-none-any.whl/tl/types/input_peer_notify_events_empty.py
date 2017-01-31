from telethon.tl.mtproto_request import MTProtoRequest


class InputPeerNotifyEventsEmpty(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    inputPeerNotifyEventsEmpty#f03064d8  = InputPeerNotifyEvents"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xf03064d8

    def __init__(self):
        super().__init__()

    def on_send(self, writer):
        writer.write_int(InputPeerNotifyEventsEmpty.constructor_id, signed=False)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return InputPeerNotifyEventsEmpty()

    def on_response(self, reader):
        pass

    def __repr__(self):
        return 'inputPeerNotifyEventsEmpty#f03064d8  = InputPeerNotifyEvents'

    def __str__(self):
        return '(inputPeerNotifyEventsEmpty (ID: 0xf03064d8) = ())'.format()
