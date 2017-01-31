from telethon.tl.mtproto_request import MTProtoRequest


class SignUpRequest(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    auth.signUp#1b067634 phone_number:string phone_code_hash:string phone_code:string first_name:string last_name:string = auth.Authorization"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x1b067634

    def __init__(self, phone_number, phone_code_hash, phone_code, first_name, last_name):
        """
        :param phone_number: Telegram type: «string».
        :param phone_code_hash: Telegram type: «string».
        :param phone_code: Telegram type: «string».
        :param first_name: Telegram type: «string».
        :param last_name: Telegram type: «string».
        """
        super().__init__()
        self.result = None
        self.confirmed = True  # Confirmed by default

        self.phone_number = phone_number
        self.phone_code_hash = phone_code_hash
        self.phone_code = phone_code
        self.first_name = first_name
        self.last_name = last_name

    def on_send(self, writer):
        writer.write_int(SignUpRequest.constructor_id, signed=False)
        writer.tgwrite_string(self.phone_number)
        writer.tgwrite_string(self.phone_code_hash)
        writer.tgwrite_string(self.phone_code)
        writer.tgwrite_string(self.first_name)
        writer.tgwrite_string(self.last_name)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return SignUpRequest(None, None, None, None, None)

    def on_response(self, reader):
        self.result = reader.tgread_object()

    def __repr__(self):
        return 'auth.signUp#1b067634 phone_number:string phone_code_hash:string phone_code:string first_name:string last_name:string = auth.Authorization'

    def __str__(self):
        return '(auth.signUp (ID: 0x1b067634) = (phone_number={}, phone_code_hash={}, phone_code={}, first_name={}, last_name={}))'.format(str(self.phone_number), str(self.phone_code_hash), str(self.phone_code), str(self.first_name), str(self.last_name))
