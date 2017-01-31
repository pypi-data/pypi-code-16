from telethon.tl.mtproto_request import MTProtoRequest


class PQInnerData(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    p_q_inner_data#83c95aec pq:string p:string q:string nonce:int128 server_nonce:int128 new_nonce:int256 = P_Q_inner_data"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x83c95aec

    def __init__(self, pq, p, q, nonce, server_nonce, new_nonce):
        """
        :param pq: Telegram type: «string».
        :param p: Telegram type: «string».
        :param q: Telegram type: «string».
        :param nonce: Telegram type: «int128».
        :param server_nonce: Telegram type: «int128».
        :param new_nonce: Telegram type: «int256».
        """
        super().__init__()

        self.pq = pq
        self.p = p
        self.q = q
        self.nonce = nonce
        self.server_nonce = server_nonce
        self.new_nonce = new_nonce

    def on_send(self, writer):
        writer.write_int(PQInnerData.constructor_id, signed=False)
        writer.tgwrite_string(self.pq)
        writer.tgwrite_string(self.p)
        writer.tgwrite_string(self.q)
        writer.write_large_int(self.nonce, bits=128)
        writer.write_large_int(self.server_nonce, bits=128)
        writer.write_large_int(self.new_nonce, bits=256)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return PQInnerData(None, None, None, None, None, None)

    def on_response(self, reader):
        self.pq = reader.tgread_string()
        self.p = reader.tgread_string()
        self.q = reader.tgread_string()
        self.nonce = reader.read_large_int(bits=128)
        self.server_nonce = reader.read_large_int(bits=128)
        self.new_nonce = reader.read_large_int(bits=256)

    def __repr__(self):
        return 'p_q_inner_data#83c95aec pq:string p:string q:string nonce:int128 server_nonce:int128 new_nonce:int256 = P_Q_inner_data'

    def __str__(self):
        return '(p_q_inner_data (ID: 0x83c95aec) = (pq={}, p={}, q={}, nonce={}, server_nonce={}, new_nonce={}))'.format(str(self.pq), str(self.p), str(self.q), str(self.nonce), str(self.server_nonce), str(self.new_nonce))
