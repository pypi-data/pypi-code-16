from telethon.tl.mtproto_request import MTProtoRequest


class DhGenOk(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    dh_gen_ok#3bcbf734 nonce:int128 server_nonce:int128 new_nonce_hash1:int128 = Set_client_DH_params_answer"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x3bcbf734

    def __init__(self, nonce, server_nonce, new_nonce_hash1):
        """
        :param nonce: Telegram type: «int128».
        :param server_nonce: Telegram type: «int128».
        :param new_nonce_hash1: Telegram type: «int128».
        """
        super().__init__()

        self.nonce = nonce
        self.server_nonce = server_nonce
        self.new_nonce_hash1 = new_nonce_hash1

    def on_send(self, writer):
        writer.write_int(DhGenOk.constructor_id, signed=False)
        writer.write_large_int(self.nonce, bits=128)
        writer.write_large_int(self.server_nonce, bits=128)
        writer.write_large_int(self.new_nonce_hash1, bits=128)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return DhGenOk(None, None, None)

    def on_response(self, reader):
        self.nonce = reader.read_large_int(bits=128)
        self.server_nonce = reader.read_large_int(bits=128)
        self.new_nonce_hash1 = reader.read_large_int(bits=128)

    def __repr__(self):
        return 'dh_gen_ok#3bcbf734 nonce:int128 server_nonce:int128 new_nonce_hash1:int128 = Set_client_DH_params_answer'

    def __str__(self):
        return '(dh_gen_ok (ID: 0x3bcbf734) = (nonce={}, server_nonce={}, new_nonce_hash1={}))'.format(str(self.nonce), str(self.server_nonce), str(self.new_nonce_hash1))
