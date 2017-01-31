from telethon.tl.mtproto_request import MTProtoRequest


class BotInlineResult(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    botInlineResult#9bebaeb9 flags:None id:string type:string title:flags.1?string description:flags.2?string url:flags.3?string thumb_url:flags.4?string content_url:flags.5?string content_type:flags.5?string w:flags.6?int h:flags.6?int duration:flags.7?int send_message:BotInlineMessage = BotInlineResult"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x9bebaeb9

    def __init__(self, id, type, send_message, title=None, description=None, url=None, thumb_url=None, content_url=None, content_type=None, w=None, h=None, duration=None):
        """
        :param id: Telegram type: «string».
        :param type: Telegram type: «string».
        :param title: Telegram type: «string».
        :param description: Telegram type: «string».
        :param url: Telegram type: «string».
        :param thumb_url: Telegram type: «string».
        :param content_url: Telegram type: «string».
        :param content_type: Telegram type: «string».
        :param w: Telegram type: «int».
        :param h: Telegram type: «int».
        :param duration: Telegram type: «int».
        :param send_message: Telegram type: «BotInlineMessage».
        """
        super().__init__()

        self.id = id
        self.type = type
        self.title = title
        self.description = description
        self.url = url
        self.thumb_url = thumb_url
        self.content_url = content_url
        self.content_type = content_type
        self.w = w
        self.h = h
        self.duration = duration
        self.send_message = send_message

    def on_send(self, writer):
        writer.write_int(BotInlineResult.constructor_id, signed=False)
        # Calculate the flags. This equals to those flag arguments which are NOT None
        flags = 0
        flags |= (1 << 1) if self.title else 0
        flags |= (1 << 2) if self.description else 0
        flags |= (1 << 3) if self.url else 0
        flags |= (1 << 4) if self.thumb_url else 0
        flags |= (1 << 5) if self.content_url else 0
        flags |= (1 << 5) if self.content_type else 0
        flags |= (1 << 6) if self.w else 0
        flags |= (1 << 6) if self.h else 0
        flags |= (1 << 7) if self.duration else 0
        writer.write_int(flags)

        writer.tgwrite_string(self.id)
        writer.tgwrite_string(self.type)
        if self.title:
            writer.tgwrite_string(self.title)

        if self.description:
            writer.tgwrite_string(self.description)

        if self.url:
            writer.tgwrite_string(self.url)

        if self.thumb_url:
            writer.tgwrite_string(self.thumb_url)

        if self.content_url:
            writer.tgwrite_string(self.content_url)

        if self.content_type:
            writer.tgwrite_string(self.content_type)

        if self.w:
            writer.write_int(self.w)

        if self.h:
            writer.write_int(self.h)

        if self.duration:
            writer.write_int(self.duration)

        self.send_message.on_send(writer)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return BotInlineResult(None, None, None, None, None, None, None, None, None, None, None, None)

    def on_response(self, reader):
        flags = reader.read_int()

        self.id = reader.tgread_string()
        self.type = reader.tgread_string()
        if (flags & (1 << 1)) != 0:
            self.title = reader.tgread_string()

        if (flags & (1 << 2)) != 0:
            self.description = reader.tgread_string()

        if (flags & (1 << 3)) != 0:
            self.url = reader.tgread_string()

        if (flags & (1 << 4)) != 0:
            self.thumb_url = reader.tgread_string()

        if (flags & (1 << 5)) != 0:
            self.content_url = reader.tgread_string()

        if (flags & (1 << 5)) != 0:
            self.content_type = reader.tgread_string()

        if (flags & (1 << 6)) != 0:
            self.w = reader.read_int()

        if (flags & (1 << 6)) != 0:
            self.h = reader.read_int()

        if (flags & (1 << 7)) != 0:
            self.duration = reader.read_int()

        self.send_message = reader.tgread_object()

    def __repr__(self):
        return 'botInlineResult#9bebaeb9 flags:None id:string type:string title:flags.1?string description:flags.2?string url:flags.3?string thumb_url:flags.4?string content_url:flags.5?string content_type:flags.5?string w:flags.6?int h:flags.6?int duration:flags.7?int send_message:BotInlineMessage = BotInlineResult'

    def __str__(self):
        return '(botInlineResult (ID: 0x9bebaeb9) = (id={}, type={}, title={}, description={}, url={}, thumb_url={}, content_url={}, content_type={}, w={}, h={}, duration={}, send_message={}))'.format(str(self.id), str(self.type), str(self.title), str(self.description), str(self.url), str(self.thumb_url), str(self.content_url), str(self.content_type), str(self.w), str(self.h), str(self.duration), str(self.send_message))
