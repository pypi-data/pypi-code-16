from telethon.tl.mtproto_request import MTProtoRequest


class ChatFull(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    chatFull#2e02a614 id:int participants:ChatParticipants chat_photo:Photo notify_settings:PeerNotifySettings exported_invite:ExportedChatInvite bot_info:Vector<BotInfo> = ChatFull"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x2e02a614

    def __init__(self, id, participants, chat_photo, notify_settings, exported_invite, bot_info):
        """
        :param id: Telegram type: «int».
        :param participants: Telegram type: «ChatParticipants».
        :param chat_photo: Telegram type: «Photo».
        :param notify_settings: Telegram type: «PeerNotifySettings».
        :param exported_invite: Telegram type: «ExportedChatInvite».
        :param bot_info: Telegram type: «BotInfo». Must be a list.
        """
        super().__init__()

        self.id = id
        self.participants = participants
        self.chat_photo = chat_photo
        self.notify_settings = notify_settings
        self.exported_invite = exported_invite
        self.bot_info = bot_info

    def on_send(self, writer):
        writer.write_int(ChatFull.constructor_id, signed=False)
        writer.write_int(self.id)
        self.participants.on_send(writer)
        self.chat_photo.on_send(writer)
        self.notify_settings.on_send(writer)
        self.exported_invite.on_send(writer)
        writer.write_int(0x1cb5c415, signed=False)  # Vector's constructor ID
        writer.write_int(len(self.bot_info))
        for bot_info_item in self.bot_info:
            bot_info_item.on_send(writer)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return ChatFull(None, None, None, None, None, None)

    def on_response(self, reader):
        self.id = reader.read_int()
        self.participants = reader.tgread_object()
        self.chat_photo = reader.tgread_object()
        self.notify_settings = reader.tgread_object()
        self.exported_invite = reader.tgread_object()
        reader.read_int()  # Vector's constructor ID
        self.bot_info = []  # Initialize an empty list
        bot_info_len = reader.read_int()
        for _ in range(bot_info_len):
            bot_info_item = reader.tgread_object()
            self.bot_info.append(bot_info_item)

    def __repr__(self):
        return 'chatFull#2e02a614 id:int participants:ChatParticipants chat_photo:Photo notify_settings:PeerNotifySettings exported_invite:ExportedChatInvite bot_info:Vector<BotInfo> = ChatFull'

    def __str__(self):
        return '(chatFull (ID: 0x2e02a614) = (id={}, participants={}, chat_photo={}, notify_settings={}, exported_invite={}, bot_info={}))'.format(str(self.id), str(self.participants), str(self.chat_photo), str(self.notify_settings), str(self.exported_invite), None if not self.bot_info else [str(_) for _ in self.bot_info])
