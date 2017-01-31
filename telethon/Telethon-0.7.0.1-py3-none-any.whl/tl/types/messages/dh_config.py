from telethon.tl.mtproto_request import MTProtoRequest


class DhConfig(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    messages.dhConfig#2c221edd g:int p:bytes version:int random:bytes = messages.DhConfig"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x2c221edd

    def __init__(self, g, p, version, random):
        """
        :param g: Telegram type: «int».
        :param p: Telegram type: «bytes».
        :param version: Telegram type: «int».
        :param random: Telegram type: «bytes».
        """
        super().__init__()

        self.g = g
        self.p = p
        self.version = version
        self.random = random

    def on_send(self, writer):
        writer.write_int(DhConfig.constructor_id, signed=False)
        writer.write_int(self.g)
        writer.tgwrite_bytes(self.p)
        writer.write_int(self.version)
        writer.tgwrite_bytes(self.random)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return DhConfig(None, None, None, None)

    def on_response(self, reader):
        self.g = reader.read_int()
        self.p = reader.tgread_bytes()
        self.version = reader.read_int()
        self.random = reader.tgread_bytes()

    def __repr__(self):
        return 'messages.dhConfig#2c221edd g:int p:bytes version:int random:bytes = messages.DhConfig'

    def __str__(self):
        return '(messages.dhConfig (ID: 0x2c221edd) = (g={}, p={}, version={}, random={}))'.format(str(self.g), str(self.p), str(self.version), str(self.random))
