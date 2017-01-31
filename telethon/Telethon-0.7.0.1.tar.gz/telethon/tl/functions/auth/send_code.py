from telethon.tl.mtproto_request import MTProtoRequest


class SendCodeRequest(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    auth.sendCode#86aef0ec flags:None allow_flashcall:flags.0?true phone_number:string current_number:flags.0?Bool api_id:int api_hash:string = auth.SentCode"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x86aef0ec

    def __init__(self, phone_number, api_id, api_hash, allow_flashcall=None, current_number=None):
        """
        :param allow_flashcall: Telegram type: «true».
        :param phone_number: Telegram type: «string».
        :param current_number: Telegram type: «Bool».
        :param api_id: Telegram type: «int».
        :param api_hash: Telegram type: «string».
        """
        super().__init__()
        self.result = None
        self.confirmed = True  # Confirmed by default

        self.allow_flashcall = allow_flashcall
        self.phone_number = phone_number
        self.current_number = current_number
        self.api_id = api_id
        self.api_hash = api_hash

    def on_send(self, writer):
        writer.write_int(SendCodeRequest.constructor_id, signed=False)
        # Calculate the flags. This equals to those flag arguments which are NOT None
        flags = 0
        flags |= (1 << 0) if self.allow_flashcall else 0
        flags |= (1 << 0) if self.current_number else 0
        writer.write_int(flags)

        writer.tgwrite_string(self.phone_number)
        if self.current_number:
            writer.tgwrite_bool(self.current_number)

        writer.write_int(self.api_id)
        writer.tgwrite_string(self.api_hash)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return SendCodeRequest(None, None, None, None, None)

    def on_response(self, reader):
        self.result = reader.tgread_object()

    def __repr__(self):
        return 'auth.sendCode#86aef0ec flags:None allow_flashcall:flags.0?true phone_number:string current_number:flags.0?Bool api_id:int api_hash:string = auth.SentCode'

    def __str__(self):
        return '(auth.sendCode (ID: 0x86aef0ec) = (allow_flashcall={}, phone_number={}, current_number={}, api_id={}, api_hash={}))'.format(str(self.allow_flashcall), str(self.phone_number), str(self.current_number), str(self.api_id), str(self.api_hash))
