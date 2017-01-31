from telethon.tl.mtproto_request import MTProtoRequest


class BotCallbackAnswer(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    messages.botCallbackAnswer#36585ea4 flags:None alert:flags.1?true has_url:flags.3?true message:flags.0?string url:flags.2?string cache_time:int = messages.BotCallbackAnswer"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x36585ea4

    def __init__(self, cache_time, alert=None, has_url=None, message=None, url=None):
        """
        :param alert: Telegram type: «true».
        :param has_url: Telegram type: «true».
        :param message: Telegram type: «string».
        :param url: Telegram type: «string».
        :param cache_time: Telegram type: «int».
        """
        super().__init__()

        self.alert = alert
        self.has_url = has_url
        self.message = message
        self.url = url
        self.cache_time = cache_time

    def on_send(self, writer):
        writer.write_int(BotCallbackAnswer.constructor_id, signed=False)
        # Calculate the flags. This equals to those flag arguments which are NOT None
        flags = 0
        flags |= (1 << 1) if self.alert else 0
        flags |= (1 << 3) if self.has_url else 0
        flags |= (1 << 0) if self.message else 0
        flags |= (1 << 2) if self.url else 0
        writer.write_int(flags)

        if self.message:
            writer.tgwrite_string(self.message)

        if self.url:
            writer.tgwrite_string(self.url)

        writer.write_int(self.cache_time)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return BotCallbackAnswer(None, None, None, None, None)

    def on_response(self, reader):
        flags = reader.read_int()

        if (flags & (1 << 1)) != 0:
            self.alert = True  # Arbitrary not-None value, no need to read since it is a flag

        if (flags & (1 << 3)) != 0:
            self.has_url = True  # Arbitrary not-None value, no need to read since it is a flag

        if (flags & (1 << 0)) != 0:
            self.message = reader.tgread_string()

        if (flags & (1 << 2)) != 0:
            self.url = reader.tgread_string()

        self.cache_time = reader.read_int()

    def __repr__(self):
        return 'messages.botCallbackAnswer#36585ea4 flags:None alert:flags.1?true has_url:flags.3?true message:flags.0?string url:flags.2?string cache_time:int = messages.BotCallbackAnswer'

    def __str__(self):
        return '(messages.botCallbackAnswer (ID: 0x36585ea4) = (alert={}, has_url={}, message={}, url={}, cache_time={}))'.format(str(self.alert), str(self.has_url), str(self.message), str(self.url), str(self.cache_time))
