from telethon.tl.mtproto_request import MTProtoRequest


class PhoneCallWaiting(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    phoneCallWaiting#1b8f4ad1 flags:None id:long access_hash:long date:date admin_id:int participant_id:int protocol:PhoneCallProtocol receive_date:flags.0?date = PhoneCall"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x1b8f4ad1

    def __init__(self, id, access_hash, date, admin_id, participant_id, protocol, receive_date=None):
        """
        :param id: Telegram type: «long».
        :param access_hash: Telegram type: «long».
        :param date: Telegram type: «date».
        :param admin_id: Telegram type: «int».
        :param participant_id: Telegram type: «int».
        :param protocol: Telegram type: «PhoneCallProtocol».
        :param receive_date: Telegram type: «date».
        """
        super().__init__()

        self.id = id
        self.access_hash = access_hash
        self.date = date
        self.admin_id = admin_id
        self.participant_id = participant_id
        self.protocol = protocol
        self.receive_date = receive_date

    def on_send(self, writer):
        writer.write_int(PhoneCallWaiting.constructor_id, signed=False)
        # Calculate the flags. This equals to those flag arguments which are NOT None
        flags = 0
        flags |= (1 << 0) if self.receive_date else 0
        writer.write_int(flags)

        writer.write_long(self.id)
        writer.write_long(self.access_hash)
        writer.tgwrite_date(self.date)
        writer.write_int(self.admin_id)
        writer.write_int(self.participant_id)
        self.protocol.on_send(writer)
        if self.receive_date:
            writer.tgwrite_date(self.receive_date)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return PhoneCallWaiting(None, None, None, None, None, None, None)

    def on_response(self, reader):
        flags = reader.read_int()

        self.id = reader.read_long()
        self.access_hash = reader.read_long()
        self.date = reader.tgread_date()
        self.admin_id = reader.read_int()
        self.participant_id = reader.read_int()
        self.protocol = reader.tgread_object()
        if (flags & (1 << 0)) != 0:
            self.receive_date = reader.tgread_date()

    def __repr__(self):
        return 'phoneCallWaiting#1b8f4ad1 flags:None id:long access_hash:long date:date admin_id:int participant_id:int protocol:PhoneCallProtocol receive_date:flags.0?date = PhoneCall'

    def __str__(self):
        return '(phoneCallWaiting (ID: 0x1b8f4ad1) = (id={}, access_hash={}, date={}, admin_id={}, participant_id={}, protocol={}, receive_date={}))'.format(str(self.id), str(self.access_hash), str(self.date), str(self.admin_id), str(self.participant_id), str(self.protocol), str(self.receive_date))
