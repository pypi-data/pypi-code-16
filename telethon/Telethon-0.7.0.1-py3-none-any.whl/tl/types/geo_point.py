from telethon.tl.mtproto_request import MTProtoRequest


class GeoPoint(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    geoPoint#2049d70c long:double lat:double = GeoPoint"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x2049d70c

    def __init__(self, long, lat):
        """
        :param long: Telegram type: «double».
        :param lat: Telegram type: «double».
        """
        super().__init__()

        self.long = long
        self.lat = lat

    def on_send(self, writer):
        writer.write_int(GeoPoint.constructor_id, signed=False)
        writer.write_double(self.long)
        writer.write_double(self.lat)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return GeoPoint(None, None)

    def on_response(self, reader):
        self.long = reader.read_double()
        self.lat = reader.read_double()

    def __repr__(self):
        return 'geoPoint#2049d70c long:double lat:double = GeoPoint'

    def __str__(self):
        return '(geoPoint (ID: 0x2049d70c) = (long={}, lat={}))'.format(str(self.long), str(self.lat))
