from telethon.tl.mtproto_request import MTProtoRequest


class PhoneCall(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    phoneCall#ffe6ab67 id:long access_hash:long date:date admin_id:int participant_id:int g_a_or_b:bytes key_fingerprint:long protocol:PhoneCallProtocol connection:PhoneConnection alternative_connections:Vector<PhoneConnection> start_date:date = PhoneCall"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xffe6ab67

    def __init__(self, id, access_hash, date, admin_id, participant_id, g_a_or_b, key_fingerprint, protocol, connection, alternative_connections, start_date):
        """
        :param id: Telegram type: «long».
        :param access_hash: Telegram type: «long».
        :param date: Telegram type: «date».
        :param admin_id: Telegram type: «int».
        :param participant_id: Telegram type: «int».
        :param g_a_or_b: Telegram type: «bytes».
        :param key_fingerprint: Telegram type: «long».
        :param protocol: Telegram type: «PhoneCallProtocol».
        :param connection: Telegram type: «PhoneConnection».
        :param alternative_connections: Telegram type: «PhoneConnection». Must be a list.
        :param start_date: Telegram type: «date».
        """
        super().__init__()

        self.id = id
        self.access_hash = access_hash
        self.date = date
        self.admin_id = admin_id
        self.participant_id = participant_id
        self.g_a_or_b = g_a_or_b
        self.key_fingerprint = key_fingerprint
        self.protocol = protocol
        self.connection = connection
        self.alternative_connections = alternative_connections
        self.start_date = start_date

    def on_send(self, writer):
        writer.write_int(PhoneCall.constructor_id, signed=False)
        writer.write_long(self.id)
        writer.write_long(self.access_hash)
        writer.tgwrite_date(self.date)
        writer.write_int(self.admin_id)
        writer.write_int(self.participant_id)
        writer.tgwrite_bytes(self.g_a_or_b)
        writer.write_long(self.key_fingerprint)
        self.protocol.on_send(writer)
        self.connection.on_send(writer)
        writer.write_int(0x1cb5c415, signed=False)  # Vector's constructor ID
        writer.write_int(len(self.alternative_connections))
        for alternative_connections_item in self.alternative_connections:
            alternative_connections_item.on_send(writer)

        writer.tgwrite_date(self.start_date)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return PhoneCall(None, None, None, None, None, None, None, None, None, None, None)

    def on_response(self, reader):
        self.id = reader.read_long()
        self.access_hash = reader.read_long()
        self.date = reader.tgread_date()
        self.admin_id = reader.read_int()
        self.participant_id = reader.read_int()
        self.g_a_or_b = reader.tgread_bytes()
        self.key_fingerprint = reader.read_long()
        self.protocol = reader.tgread_object()
        self.connection = reader.tgread_object()
        reader.read_int()  # Vector's constructor ID
        self.alternative_connections = []  # Initialize an empty list
        alternative_connections_len = reader.read_int()
        for _ in range(alternative_connections_len):
            alternative_connections_item = reader.tgread_object()
            self.alternative_connections.append(alternative_connections_item)

        self.start_date = reader.tgread_date()

    def __repr__(self):
        return 'phoneCall#ffe6ab67 id:long access_hash:long date:date admin_id:int participant_id:int g_a_or_b:bytes key_fingerprint:long protocol:PhoneCallProtocol connection:PhoneConnection alternative_connections:Vector<PhoneConnection> start_date:date = PhoneCall'

    def __str__(self):
        return '(phoneCall (ID: 0xffe6ab67) = (id={}, access_hash={}, date={}, admin_id={}, participant_id={}, g_a_or_b={}, key_fingerprint={}, protocol={}, connection={}, alternative_connections={}, start_date={}))'.format(str(self.id), str(self.access_hash), str(self.date), str(self.admin_id), str(self.participant_id), str(self.g_a_or_b), str(self.key_fingerprint), str(self.protocol), str(self.connection), None if not self.alternative_connections else [str(_) for _ in self.alternative_connections], str(self.start_date))
