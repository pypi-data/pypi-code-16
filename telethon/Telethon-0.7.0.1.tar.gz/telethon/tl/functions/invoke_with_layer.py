from telethon.tl.mtproto_request import MTProtoRequest


class InvokeWithLayerRequest(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    invokeWithLayer#da9b0d0d {X:Type} layer:int query:!X = X"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xda9b0d0d

    def __init__(self, layer, query):
        """
        :param layer: Telegram type: «int».
        :param query: Telegram type: «X». This should be another MTProtoRequest.
        """
        super().__init__()
        self.result = None
        self.confirmed = True  # Confirmed by default

        self.layer = layer
        self.query = query

    def on_send(self, writer):
        writer.write_int(InvokeWithLayerRequest.constructor_id, signed=False)
        writer.write_int(self.layer)
        self.query.on_send(writer)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return InvokeWithLayerRequest(None, None)

    def on_response(self, reader):
        self.result = reader.tgread_object()

    def __repr__(self):
        return 'invokeWithLayer#da9b0d0d {X:Type} layer:int query:!X = X'

    def __str__(self):
        return '(invokeWithLayer (ID: 0xda9b0d0d) = (layer={}, query={}))'.format(str(self.layer), str(self.query))
