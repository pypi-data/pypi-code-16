from telethon.tl.mtproto_request import MTProtoRequest


class InputGeoPoint(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    inputGeoPoint#f3b7acc9 lat:double long:double = InputGeoPoint"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xf3b7acc9

    def __init__(self, lat, long):
        """
        :param lat: Telegram type: «double».
        :param long: Telegram type: «double».
        """
        super().__init__()

        self.lat = lat
        self.long = long

    def on_send(self, writer):
        writer.write_int(InputGeoPoint.constructor_id, signed=False)
        writer.write_double(self.lat)
        writer.write_double(self.long)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return InputGeoPoint(None, None)

    def on_response(self, reader):
        self.lat = reader.read_double()
        self.long = reader.read_double()

    def __repr__(self):
        return 'inputGeoPoint#f3b7acc9 lat:double long:double = InputGeoPoint'

    def __str__(self):
        return '(inputGeoPoint (ID: 0xf3b7acc9) = (lat={}, long={}))'.format(str(self.lat), str(self.long))
