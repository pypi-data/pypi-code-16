from telethon.tl.mtproto_request import MTProtoRequest


class NoPassword(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    account.noPassword#96dabc18 new_salt:bytes email_unconfirmed_pattern:string = account.Password"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0x96dabc18

    def __init__(self, new_salt, email_unconfirmed_pattern):
        """
        :param new_salt: Telegram type: «bytes».
        :param email_unconfirmed_pattern: Telegram type: «string».
        """
        super().__init__()

        self.new_salt = new_salt
        self.email_unconfirmed_pattern = email_unconfirmed_pattern

    def on_send(self, writer):
        writer.write_int(NoPassword.constructor_id, signed=False)
        writer.tgwrite_bytes(self.new_salt)
        writer.tgwrite_string(self.email_unconfirmed_pattern)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return NoPassword(None, None)

    def on_response(self, reader):
        self.new_salt = reader.tgread_bytes()
        self.email_unconfirmed_pattern = reader.tgread_string()

    def __repr__(self):
        return 'account.noPassword#96dabc18 new_salt:bytes email_unconfirmed_pattern:string = account.Password'

    def __str__(self):
        return '(account.noPassword (ID: 0x96dabc18) = (new_salt={}, email_unconfirmed_pattern={}))'.format(str(self.new_salt), str(self.email_unconfirmed_pattern))
