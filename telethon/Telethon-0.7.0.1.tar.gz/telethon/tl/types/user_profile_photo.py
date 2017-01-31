from telethon.tl.mtproto_request import MTProtoRequest


class UserProfilePhoto(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    userProfilePhoto#d559d8c8 photo_id:long photo_small:FileLocation photo_big:FileLocation = UserProfilePhoto"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xd559d8c8

    def __init__(self, photo_id, photo_small, photo_big):
        """
        :param photo_id: Telegram type: «long».
        :param photo_small: Telegram type: «FileLocation».
        :param photo_big: Telegram type: «FileLocation».
        """
        super().__init__()

        self.photo_id = photo_id
        self.photo_small = photo_small
        self.photo_big = photo_big

    def on_send(self, writer):
        writer.write_int(UserProfilePhoto.constructor_id, signed=False)
        writer.write_long(self.photo_id)
        self.photo_small.on_send(writer)
        self.photo_big.on_send(writer)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return UserProfilePhoto(None, None, None)

    def on_response(self, reader):
        self.photo_id = reader.read_long()
        self.photo_small = reader.tgread_object()
        self.photo_big = reader.tgread_object()

    def __repr__(self):
        return 'userProfilePhoto#d559d8c8 photo_id:long photo_small:FileLocation photo_big:FileLocation = UserProfilePhoto'

    def __str__(self):
        return '(userProfilePhoto (ID: 0xd559d8c8) = (photo_id={}, photo_small={}, photo_big={}))'.format(str(self.photo_id), str(self.photo_small), str(self.photo_big))
