from telethon.tl.mtproto_request import MTProtoRequest


class Game(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    game#bdf9653b flags:None id:long access_hash:long short_name:string title:string description:string photo:Photo document:flags.0?Document = Game"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xbdf9653b

    def __init__(self, id, access_hash, short_name, title, description, photo, document=None):
        """
        :param id: Telegram type: «long».
        :param access_hash: Telegram type: «long».
        :param short_name: Telegram type: «string».
        :param title: Telegram type: «string».
        :param description: Telegram type: «string».
        :param photo: Telegram type: «Photo».
        :param document: Telegram type: «Document».
        """
        super().__init__()

        self.id = id
        self.access_hash = access_hash
        self.short_name = short_name
        self.title = title
        self.description = description
        self.photo = photo
        self.document = document

    def on_send(self, writer):
        writer.write_int(Game.constructor_id, signed=False)
        # Calculate the flags. This equals to those flag arguments which are NOT None
        flags = 0
        flags |= (1 << 0) if self.document else 0
        writer.write_int(flags)

        writer.write_long(self.id)
        writer.write_long(self.access_hash)
        writer.tgwrite_string(self.short_name)
        writer.tgwrite_string(self.title)
        writer.tgwrite_string(self.description)
        self.photo.on_send(writer)
        if self.document:
            self.document.on_send(writer)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return Game(None, None, None, None, None, None, None)

    def on_response(self, reader):
        flags = reader.read_int()

        self.id = reader.read_long()
        self.access_hash = reader.read_long()
        self.short_name = reader.tgread_string()
        self.title = reader.tgread_string()
        self.description = reader.tgread_string()
        self.photo = reader.tgread_object()
        if (flags & (1 << 0)) != 0:
            self.document = reader.tgread_object()

    def __repr__(self):
        return 'game#bdf9653b flags:None id:long access_hash:long short_name:string title:string description:string photo:Photo document:flags.0?Document = Game'

    def __str__(self):
        return '(game (ID: 0xbdf9653b) = (id={}, access_hash={}, short_name={}, title={}, description={}, photo={}, document={}))'.format(str(self.id), str(self.access_hash), str(self.short_name), str(self.title), str(self.description), str(self.photo), str(self.document))
