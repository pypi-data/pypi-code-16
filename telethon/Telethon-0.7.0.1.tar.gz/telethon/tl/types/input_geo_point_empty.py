from telethon.tl.mtproto_request import MTProtoRequest


class InputGeoPointEmpty(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    inputGeoPointEmpty#e4c123d6  = InputGeoPoint"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xe4c123d6

    def __init__(self):
        super().__init__()

    def on_send(self, writer):
        writer.write_int(InputGeoPointEmpty.constructor_id, signed=False)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return InputGeoPointEmpty()

    def on_response(self, reader):
        pass

    def __repr__(self):
        return 'inputGeoPointEmpty#e4c123d6  = InputGeoPoint'

    def __str__(self):
        return '(inputGeoPointEmpty (ID: 0xe4c123d6) = ())'.format()
