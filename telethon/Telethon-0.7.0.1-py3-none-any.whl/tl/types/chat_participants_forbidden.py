from telethon.tl.mtproto_request import MTProtoRequest


class ChatParticipantsForbidden(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    chatParticipantsForbidden#fc900c2b flags:None chat_id:int self_participant:flags.0?ChatParticipant = ChatParticipants"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xfc900c2b

    def __init__(self, chat_id, self_participant=None):
        """
        :param chat_id: Telegram type: «int».
        :param self_participant: Telegram type: «ChatParticipant».
        """
        super().__init__()

        self.chat_id = chat_id
        self.self_participant = self_participant

    def on_send(self, writer):
        writer.write_int(ChatParticipantsForbidden.constructor_id, signed=False)
        # Calculate the flags. This equals to those flag arguments which are NOT None
        flags = 0
        flags |= (1 << 0) if self.self_participant else 0
        writer.write_int(flags)

        writer.write_int(self.chat_id)
        if self.self_participant:
            self.self_participant.on_send(writer)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return ChatParticipantsForbidden(None, None)

    def on_response(self, reader):
        flags = reader.read_int()

        self.chat_id = reader.read_int()
        if (flags & (1 << 0)) != 0:
            self.self_participant = reader.tgread_object()

    def __repr__(self):
        return 'chatParticipantsForbidden#fc900c2b flags:None chat_id:int self_participant:flags.0?ChatParticipant = ChatParticipants'

    def __str__(self):
        return '(chatParticipantsForbidden (ID: 0xfc900c2b) = (chat_id={}, self_participant={}))'.format(str(self.chat_id), str(self.self_participant))
