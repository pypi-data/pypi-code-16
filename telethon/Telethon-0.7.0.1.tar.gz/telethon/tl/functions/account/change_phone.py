from telethon.tl.mtproto_request import MTProtoRequest


class ChangePhoneRequest(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    account.changePhone#70c32edb phone_number:string phone_code_hash:string phone_code:string = User"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x70c32edb

    def __init__(self, phone_number, phone_code_hash, phone_code):
        """
        :param phone_number: Telegram type: «string».
        :param phone_code_hash: Telegram type: «string».
        :param phone_code: Telegram type: «string».
        """
        super().__init__()
        self.result = None
        self.confirmed = True  # Confirmed by default

        self.phone_number = phone_number
        self.phone_code_hash = phone_code_hash
        self.phone_code = phone_code

    def on_send(self, writer):
        writer.write_int(ChangePhoneRequest.constructor_id, signed=False)
        writer.tgwrite_string(self.phone_number)
        writer.tgwrite_string(self.phone_code_hash)
        writer.tgwrite_string(self.phone_code)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return ChangePhoneRequest(None, None, None)

    def on_response(self, reader):
        self.result = reader.tgread_object()

    def __repr__(self):
        return 'account.changePhone#70c32edb phone_number:string phone_code_hash:string phone_code:string = User'

    def __str__(self):
        return '(account.changePhone (ID: 0x70c32edb) = (phone_number={}, phone_code_hash={}, phone_code={}))'.format(str(self.phone_number), str(self.phone_code_hash), str(self.phone_code))
