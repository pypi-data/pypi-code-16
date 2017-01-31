from telethon.tl.mtproto_request import MTProtoRequest


class AcceptEncryptionRequest(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    messages.acceptEncryption#3dbc0415 peer:InputEncryptedChat g_b:bytes key_fingerprint:long = EncryptedChat"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x3dbc0415

    def __init__(self, peer, g_b, key_fingerprint):
        """
        :param peer: Telegram type: «InputEncryptedChat».
        :param g_b: Telegram type: «bytes».
        :param key_fingerprint: Telegram type: «long».
        """
        super().__init__()
        self.result = None
        self.confirmed = True  # Confirmed by default

        self.peer = peer
        self.g_b = g_b
        self.key_fingerprint = key_fingerprint

    def on_send(self, writer):
        writer.write_int(AcceptEncryptionRequest.constructor_id, signed=False)
        self.peer.on_send(writer)
        writer.tgwrite_bytes(self.g_b)
        writer.write_long(self.key_fingerprint)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return AcceptEncryptionRequest(None, None, None)

    def on_response(self, reader):
        self.result = reader.tgread_object()

    def __repr__(self):
        return 'messages.acceptEncryption#3dbc0415 peer:InputEncryptedChat g_b:bytes key_fingerprint:long = EncryptedChat'

    def __str__(self):
        return '(messages.acceptEncryption (ID: 0x3dbc0415) = (peer={}, g_b={}, key_fingerprint={}))'.format(str(self.peer), str(self.g_b), str(self.key_fingerprint))
