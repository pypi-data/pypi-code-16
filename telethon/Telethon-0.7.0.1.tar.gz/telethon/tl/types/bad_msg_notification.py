from telethon.tl.mtproto_request import MTProtoRequest


class BadMsgNotification(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    bad_msg_notification#a7eff811 bad_msg_id:long bad_msg_seqno:int error_code:int = BadMsgNotification"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xa7eff811

    def __init__(self, bad_msg_id, bad_msg_seqno, error_code):
        """
        :param bad_msg_id: Telegram type: «long».
        :param bad_msg_seqno: Telegram type: «int».
        :param error_code: Telegram type: «int».
        """
        super().__init__()

        self.bad_msg_id = bad_msg_id
        self.bad_msg_seqno = bad_msg_seqno
        self.error_code = error_code

    def on_send(self, writer):
        writer.write_int(BadMsgNotification.constructor_id, signed=False)
        writer.write_long(self.bad_msg_id)
        writer.write_int(self.bad_msg_seqno)
        writer.write_int(self.error_code)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return BadMsgNotification(None, None, None)

    def on_response(self, reader):
        self.bad_msg_id = reader.read_long()
        self.bad_msg_seqno = reader.read_int()
        self.error_code = reader.read_int()

    def __repr__(self):
        return 'bad_msg_notification#a7eff811 bad_msg_id:long bad_msg_seqno:int error_code:int = BadMsgNotification'

    def __str__(self):
        return '(bad_msg_notification (ID: 0xa7eff811) = (bad_msg_id={}, bad_msg_seqno={}, error_code={}))'.format(str(self.bad_msg_id), str(self.bad_msg_seqno), str(self.error_code))
