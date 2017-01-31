from telethon.tl.mtproto_request import MTProtoRequest


class SendEncryptedServiceRequest(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    messages.sendEncryptedService#32d439a4 peer:InputEncryptedChat random_id:long data:bytes = messages.SentEncryptedMessage"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x32d439a4

    def __init__(self, peer, random_id, data):
        """
        :param peer: Telegram type: «InputEncryptedChat».
        :param random_id: Telegram type: «long».
        :param data: Telegram type: «bytes».
        """
        super().__init__()
        self.result = None
        self.confirmed = True  # Confirmed by default

        self.peer = peer
        self.random_id = random_id
        self.data = data

    def on_send(self, writer):
        writer.write_int(SendEncryptedServiceRequest.constructor_id, signed=False)
        self.peer.on_send(writer)
        writer.write_long(self.random_id)
        writer.tgwrite_bytes(self.data)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return SendEncryptedServiceRequest(None, None, None)

    def on_response(self, reader):
        self.result = reader.tgread_object()

    def __repr__(self):
        return 'messages.sendEncryptedService#32d439a4 peer:InputEncryptedChat random_id:long data:bytes = messages.SentEncryptedMessage'

    def __str__(self):
        return '(messages.sendEncryptedService (ID: 0x32d439a4) = (peer={}, random_id={}, data={}))'.format(str(self.peer), str(self.random_id), str(self.data))
