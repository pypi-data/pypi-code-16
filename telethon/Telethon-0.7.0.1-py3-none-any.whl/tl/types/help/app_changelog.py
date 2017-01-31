from telethon.tl.mtproto_request import MTProtoRequest


class AppChangelog(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    help.appChangelog#2a137e7c message:string media:MessageMedia entities:Vector<MessageEntity> = help.AppChangelog"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x2a137e7c

    def __init__(self, message, media, entities):
        """
        :param message: Telegram type: «string».
        :param media: Telegram type: «MessageMedia».
        :param entities: Telegram type: «MessageEntity». Must be a list.
        """
        super().__init__()

        self.message = message
        self.media = media
        self.entities = entities

    def on_send(self, writer):
        writer.write_int(AppChangelog.constructor_id, signed=False)
        writer.tgwrite_string(self.message)
        self.media.on_send(writer)
        writer.write_int(0x1cb5c415, signed=False)  # Vector's constructor ID
        writer.write_int(len(self.entities))
        for entities_item in self.entities:
            entities_item.on_send(writer)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return AppChangelog(None, None, None)

    def on_response(self, reader):
        self.message = reader.tgread_string()
        self.media = reader.tgread_object()
        reader.read_int()  # Vector's constructor ID
        self.entities = []  # Initialize an empty list
        entities_len = reader.read_int()
        for _ in range(entities_len):
            entities_item = reader.tgread_object()
            self.entities.append(entities_item)

    def __repr__(self):
        return 'help.appChangelog#2a137e7c message:string media:MessageMedia entities:Vector<MessageEntity> = help.AppChangelog'

    def __str__(self):
        return '(help.appChangelog (ID: 0x2a137e7c) = (message={}, media={}, entities={}))'.format(str(self.message), str(self.media), None if not self.entities else [str(_) for _ in self.entities])
