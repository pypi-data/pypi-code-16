from telethon.tl.mtproto_request import MTProtoRequest


class PrivacyValueDisallowUsers(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    privacyValueDisallowUsers#0c7f49b7 users:Vector<int> = PrivacyRule"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xc7f49b7

    def __init__(self, users):
        """
        :param users: Telegram type: «int». Must be a list.
        """
        super().__init__()

        self.users = users

    def on_send(self, writer):
        writer.write_int(PrivacyValueDisallowUsers.constructor_id, signed=False)
        writer.write_int(0x1cb5c415, signed=False)  # Vector's constructor ID
        writer.write_int(len(self.users))
        for users_item in self.users:
            writer.write_int(users_item)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return PrivacyValueDisallowUsers(None)

    def on_response(self, reader):
        reader.read_int()  # Vector's constructor ID
        self.users = []  # Initialize an empty list
        users_len = reader.read_int()
        for _ in range(users_len):
            users_item = reader.read_int()
            self.users.append(users_item)

    def __repr__(self):
        return 'privacyValueDisallowUsers#0c7f49b7 users:Vector<int> = PrivacyRule'

    def __str__(self):
        return '(privacyValueDisallowUsers (ID: 0xc7f49b7) = (users={}))'.format(None if not self.users else [str(_) for _ in self.users])
