from telethon.tl.mtproto_request import MTProtoRequest


class AppChangelogEmpty(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    help.appChangelogEmpty#af7e0394  = help.AppChangelog"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xaf7e0394

    def __init__(self):
        super().__init__()

    def on_send(self, writer):
        writer.write_int(AppChangelogEmpty.constructor_id, signed=False)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return AppChangelogEmpty()

    def on_response(self, reader):
        pass

    def __repr__(self):
        return 'help.appChangelogEmpty#af7e0394  = help.AppChangelog'

    def __str__(self):
        return '(help.appChangelogEmpty (ID: 0xaf7e0394) = ())'.format()
