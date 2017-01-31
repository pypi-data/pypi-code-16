from telethon.tl.mtproto_request import MTProtoRequest


class InputMediaUploadedThumbDocument(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    inputMediaUploadedThumbDocument#50d88cae flags:None file:InputFile thumb:InputFile mime_type:string attributes:Vector<DocumentAttribute> caption:string stickers:flags.0?Vector<InputDocument> = InputMedia"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x50d88cae

    def __init__(self, file, thumb, mime_type, attributes, caption, stickers=None):
        """
        :param file: Telegram type: «InputFile».
        :param thumb: Telegram type: «InputFile».
        :param mime_type: Telegram type: «string».
        :param attributes: Telegram type: «DocumentAttribute». Must be a list.
        :param caption: Telegram type: «string».
        :param stickers: Telegram type: «InputDocument». Must be a list.
        """
        super().__init__()

        self.file = file
        self.thumb = thumb
        self.mime_type = mime_type
        self.attributes = attributes
        self.caption = caption
        self.stickers = stickers

    def on_send(self, writer):
        writer.write_int(InputMediaUploadedThumbDocument.constructor_id, signed=False)
        # Calculate the flags. This equals to those flag arguments which are NOT None
        flags = 0
        flags |= (1 << 0) if self.stickers else 0
        writer.write_int(flags)

        self.file.on_send(writer)
        self.thumb.on_send(writer)
        writer.tgwrite_string(self.mime_type)
        writer.write_int(0x1cb5c415, signed=False)  # Vector's constructor ID
        writer.write_int(len(self.attributes))
        for attributes_item in self.attributes:
            attributes_item.on_send(writer)

        writer.tgwrite_string(self.caption)
        if self.stickers:
            writer.write_int(0x1cb5c415, signed=False)  # Vector's constructor ID
            writer.write_int(len(self.stickers))
            for stickers_item in self.stickers:
                if stickers_item:
                    stickers_item.on_send(writer)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return InputMediaUploadedThumbDocument(None, None, None, None, None, None)

    def on_response(self, reader):
        flags = reader.read_int()

        self.file = reader.tgread_object()
        self.thumb = reader.tgread_object()
        self.mime_type = reader.tgread_string()
        reader.read_int()  # Vector's constructor ID
        self.attributes = []  # Initialize an empty list
        attributes_len = reader.read_int()
        for _ in range(attributes_len):
            attributes_item = reader.tgread_object()
            self.attributes.append(attributes_item)

        self.caption = reader.tgread_string()
        if (flags & (1 << 0)) != 0:
            reader.read_int()  # Vector's constructor ID
            self.stickers = []  # Initialize an empty list
            stickers_len = reader.read_int()
            for _ in range(stickers_len):
                stickers_item = reader.tgread_object()
                self.stickers.append(stickers_item)

    def __repr__(self):
        return 'inputMediaUploadedThumbDocument#50d88cae flags:None file:InputFile thumb:InputFile mime_type:string attributes:Vector<DocumentAttribute> caption:string stickers:flags.0?Vector<InputDocument> = InputMedia'

    def __str__(self):
        return '(inputMediaUploadedThumbDocument (ID: 0x50d88cae) = (file={}, thumb={}, mime_type={}, attributes={}, caption={}, stickers={}))'.format(str(self.file), str(self.thumb), str(self.mime_type), None if not self.attributes else [str(_) for _ in self.attributes], str(self.caption), None if not self.stickers else [str(_) for _ in self.stickers])
