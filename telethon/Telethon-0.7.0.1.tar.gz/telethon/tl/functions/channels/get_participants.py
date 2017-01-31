from telethon.tl.mtproto_request import MTProtoRequest


class GetParticipantsRequest(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    channels.getParticipants#24d98f92 channel:InputChannel filter:ChannelParticipantsFilter offset:int limit:int = channels.ChannelParticipants"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x24d98f92

    def __init__(self, channel, filter, offset, limit):
        """
        :param channel: Telegram type: «InputChannel».
        :param filter: Telegram type: «ChannelParticipantsFilter».
        :param offset: Telegram type: «int».
        :param limit: Telegram type: «int».
        """
        super().__init__()
        self.result = None
        self.confirmed = True  # Confirmed by default

        self.channel = channel
        self.filter = filter
        self.offset = offset
        self.limit = limit

    def on_send(self, writer):
        writer.write_int(GetParticipantsRequest.constructor_id, signed=False)
        self.channel.on_send(writer)
        self.filter.on_send(writer)
        writer.write_int(self.offset)
        writer.write_int(self.limit)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return GetParticipantsRequest(None, None, None, None)

    def on_response(self, reader):
        self.result = reader.tgread_object()

    def __repr__(self):
        return 'channels.getParticipants#24d98f92 channel:InputChannel filter:ChannelParticipantsFilter offset:int limit:int = channels.ChannelParticipants'

    def __str__(self):
        return '(channels.getParticipants (ID: 0x24d98f92) = (channel={}, filter={}, offset={}, limit={}))'.format(str(self.channel), str(self.filter), str(self.offset), str(self.limit))
