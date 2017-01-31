from telethon.tl.mtproto_request import MTProtoRequest


class ContactLinkNone(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    contactLinkNone#feedd3ad  = ContactLink"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xfeedd3ad

    def __init__(self):
        super().__init__()

    def on_send(self, writer):
        writer.write_int(ContactLinkNone.constructor_id, signed=False)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return ContactLinkNone()

    def on_response(self, reader):
        pass

    def __repr__(self):
        return 'contactLinkNone#feedd3ad  = ContactLink'

    def __str__(self):
        return '(contactLinkNone (ID: 0xfeedd3ad) = ())'.format()
