from telethon.tl.mtproto_request import MTProtoRequest


class MsgsStateReq(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    msgs_state_req#da69fb52 msg_ids:Vector<long> = MsgsStateReq"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xda69fb52

    def __init__(self, msg_ids):
        """
        :param msg_ids: Telegram type: «long». Must be a list.
        """
        super().__init__()

        self.msg_ids = msg_ids

    def on_send(self, writer):
        writer.write_int(MsgsStateReq.constructor_id, signed=False)
        writer.write_int(0x1cb5c415, signed=False)  # Vector's constructor ID
        writer.write_int(len(self.msg_ids))
        for msg_ids_item in self.msg_ids:
            writer.write_long(msg_ids_item)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return MsgsStateReq(None)

    def on_response(self, reader):
        reader.read_int()  # Vector's constructor ID
        self.msg_ids = []  # Initialize an empty list
        msg_ids_len = reader.read_int()
        for _ in range(msg_ids_len):
            msg_ids_item = reader.read_long()
            self.msg_ids.append(msg_ids_item)

    def __repr__(self):
        return 'msgs_state_req#da69fb52 msg_ids:Vector<long> = MsgsStateReq'

    def __str__(self):
        return '(msgs_state_req (ID: 0xda69fb52) = (msg_ids={}))'.format(None if not self.msg_ids else [str(_) for _ in self.msg_ids])
