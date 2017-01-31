from telethon.tl.mtproto_request import MTProtoRequest


class EditMessageRequest(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    messages.editMessage#ce91e4ca flags:None no_webpage:flags.1?true peer:InputPeer id:int message:flags.11?string reply_markup:flags.2?ReplyMarkup entities:flags.3?Vector<MessageEntity> = Updates"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xce91e4ca

    def __init__(self, peer, id, no_webpage=None, message=None, reply_markup=None, entities=None):
        """
        :param no_webpage: Telegram type: «true».
        :param peer: Telegram type: «InputPeer».
        :param id: Telegram type: «int».
        :param message: Telegram type: «string».
        :param reply_markup: Telegram type: «ReplyMarkup».
        :param entities: Telegram type: «MessageEntity». Must be a list.
        """
        super().__init__()
        self.result = None
        self.confirmed = True  # Confirmed by default

        self.no_webpage = no_webpage
        self.peer = peer
        self.id = id
        self.message = message
        self.reply_markup = reply_markup
        self.entities = entities

    def on_send(self, writer):
        writer.write_int(EditMessageRequest.constructor_id, signed=False)
        # Calculate the flags. This equals to those flag arguments which are NOT None
        flags = 0
        flags |= (1 << 1) if self.no_webpage else 0
        flags |= (1 << 11) if self.message else 0
        flags |= (1 << 2) if self.reply_markup else 0
        flags |= (1 << 3) if self.entities else 0
        writer.write_int(flags)

        self.peer.on_send(writer)
        writer.write_int(self.id)
        if self.message:
            writer.tgwrite_string(self.message)

        if self.reply_markup:
            self.reply_markup.on_send(writer)

        if self.entities:
            writer.write_int(0x1cb5c415, signed=False)  # Vector's constructor ID
            writer.write_int(len(self.entities))
            for entities_item in self.entities:
                if entities_item:
                    entities_item.on_send(writer)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return EditMessageRequest(None, None, None, None, None, None)

    def on_response(self, reader):
        self.result = reader.tgread_object()

    def __repr__(self):
        return 'messages.editMessage#ce91e4ca flags:None no_webpage:flags.1?true peer:InputPeer id:int message:flags.11?string reply_markup:flags.2?ReplyMarkup entities:flags.3?Vector<MessageEntity> = Updates'

    def __str__(self):
        return '(messages.editMessage (ID: 0xce91e4ca) = (no_webpage={}, peer={}, id={}, message={}, reply_markup={}, entities={}))'.format(str(self.no_webpage), str(self.peer), str(self.id), str(self.message), str(self.reply_markup), None if not self.entities else [str(_) for _ in self.entities])
