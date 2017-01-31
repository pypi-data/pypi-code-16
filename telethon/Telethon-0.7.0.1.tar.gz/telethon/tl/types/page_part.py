from telethon.tl.mtproto_request import MTProtoRequest


class PagePart(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    pagePart#8dee6c44 blocks:Vector<PageBlock> photos:Vector<Photo> videos:Vector<Document> = Page"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x8dee6c44

    def __init__(self, blocks, photos, videos):
        """
        :param blocks: Telegram type: «PageBlock». Must be a list.
        :param photos: Telegram type: «Photo». Must be a list.
        :param videos: Telegram type: «Document». Must be a list.
        """
        super().__init__()

        self.blocks = blocks
        self.photos = photos
        self.videos = videos

    def on_send(self, writer):
        writer.write_int(PagePart.constructor_id, signed=False)
        writer.write_int(0x1cb5c415, signed=False)  # Vector's constructor ID
        writer.write_int(len(self.blocks))
        for blocks_item in self.blocks:
            blocks_item.on_send(writer)

        writer.write_int(0x1cb5c415, signed=False)  # Vector's constructor ID
        writer.write_int(len(self.photos))
        for photos_item in self.photos:
            photos_item.on_send(writer)

        writer.write_int(0x1cb5c415, signed=False)  # Vector's constructor ID
        writer.write_int(len(self.videos))
        for videos_item in self.videos:
            videos_item.on_send(writer)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return PagePart(None, None, None)

    def on_response(self, reader):
        reader.read_int()  # Vector's constructor ID
        self.blocks = []  # Initialize an empty list
        blocks_len = reader.read_int()
        for _ in range(blocks_len):
            blocks_item = reader.tgread_object()
            self.blocks.append(blocks_item)

        reader.read_int()  # Vector's constructor ID
        self.photos = []  # Initialize an empty list
        photos_len = reader.read_int()
        for _ in range(photos_len):
            photos_item = reader.tgread_object()
            self.photos.append(photos_item)

        reader.read_int()  # Vector's constructor ID
        self.videos = []  # Initialize an empty list
        videos_len = reader.read_int()
        for _ in range(videos_len):
            videos_item = reader.tgread_object()
            self.videos.append(videos_item)

    def __repr__(self):
        return 'pagePart#8dee6c44 blocks:Vector<PageBlock> photos:Vector<Photo> videos:Vector<Document> = Page'

    def __str__(self):
        return '(pagePart (ID: 0x8dee6c44) = (blocks={}, photos={}, videos={}))'.format(None if not self.blocks else [str(_) for _ in self.blocks], None if not self.photos else [str(_) for _ in self.photos], None if not self.videos else [str(_) for _ in self.videos])
