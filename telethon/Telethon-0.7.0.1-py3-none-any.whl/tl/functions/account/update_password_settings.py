from telethon.tl.mtproto_request import MTProtoRequest


class UpdatePasswordSettingsRequest(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    account.updatePasswordSettings#fa7c4b86 current_password_hash:bytes new_settings:account.PasswordInputSettings = Bool"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xfa7c4b86

    def __init__(self, current_password_hash, new_settings):
        """
        :param current_password_hash: Telegram type: «bytes».
        :param new_settings: Telegram type: «account.PasswordInputSettings».
        """
        super().__init__()
        self.result = None
        self.confirmed = True  # Confirmed by default

        self.current_password_hash = current_password_hash
        self.new_settings = new_settings

    def on_send(self, writer):
        writer.write_int(UpdatePasswordSettingsRequest.constructor_id, signed=False)
        writer.tgwrite_bytes(self.current_password_hash)
        self.new_settings.on_send(writer)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return UpdatePasswordSettingsRequest(None, None)

    def on_response(self, reader):
        self.result = reader.tgread_object()

    def __repr__(self):
        return 'account.updatePasswordSettings#fa7c4b86 current_password_hash:bytes new_settings:account.PasswordInputSettings = Bool'

    def __str__(self):
        return '(account.updatePasswordSettings (ID: 0xfa7c4b86) = (current_password_hash={}, new_settings={}))'.format(str(self.current_password_hash), str(self.new_settings))
