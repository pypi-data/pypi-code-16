from telethon.tl.mtproto_request import MTProtoRequest


class Channel(MTProtoRequest):
    """Class generated by TLObjects' generator. All changes will be ERASED. Original .tl definition below.
    channel#a14dca52 flags:None creator:flags.0?true kicked:flags.1?true left:flags.2?true editor:flags.3?true moderator:flags.4?true broadcast:flags.5?true verified:flags.7?true megagroup:flags.8?true restricted:flags.9?true democracy:flags.10?true signatures:flags.11?true min:flags.12?true id:int access_hash:flags.13?long title:string username:flags.6?string photo:ChatPhoto date:date version:int restriction_reason:flags.9?string = Chat"""

    # Telegram's constructor ID (and unique identifier) for this class
    constructor_id = 0xa14dca52

    def __init__(self, id, title, photo, date, version, creator=None, kicked=None, left=None, editor=None, moderator=None, broadcast=None, verified=None, megagroup=None, restricted=None, democracy=None, signatures=None, min=None, access_hash=None, username=None, restriction_reason=None):
        """
        :param creator: Telegram type: «true».
        :param kicked: Telegram type: «true».
        :param left: Telegram type: «true».
        :param editor: Telegram type: «true».
        :param moderator: Telegram type: «true».
        :param broadcast: Telegram type: «true».
        :param verified: Telegram type: «true».
        :param megagroup: Telegram type: «true».
        :param restricted: Telegram type: «true».
        :param democracy: Telegram type: «true».
        :param signatures: Telegram type: «true».
        :param min: Telegram type: «true».
        :param id: Telegram type: «int».
        :param access_hash: Telegram type: «long».
        :param title: Telegram type: «string».
        :param username: Telegram type: «string».
        :param photo: Telegram type: «ChatPhoto».
        :param date: Telegram type: «date».
        :param version: Telegram type: «int».
        :param restriction_reason: Telegram type: «string».
        """
        super().__init__()

        self.creator = creator
        self.kicked = kicked
        self.left = left
        self.editor = editor
        self.moderator = moderator
        self.broadcast = broadcast
        self.verified = verified
        self.megagroup = megagroup
        self.restricted = restricted
        self.democracy = democracy
        self.signatures = signatures
        self.min = min
        self.id = id
        self.access_hash = access_hash
        self.title = title
        self.username = username
        self.photo = photo
        self.date = date
        self.version = version
        self.restriction_reason = restriction_reason

    def on_send(self, writer):
        writer.write_int(Channel.constructor_id, signed=False)
        # Calculate the flags. This equals to those flag arguments which are NOT None
        flags = 0
        flags |= (1 << 0) if self.creator else 0
        flags |= (1 << 1) if self.kicked else 0
        flags |= (1 << 2) if self.left else 0
        flags |= (1 << 3) if self.editor else 0
        flags |= (1 << 4) if self.moderator else 0
        flags |= (1 << 5) if self.broadcast else 0
        flags |= (1 << 7) if self.verified else 0
        flags |= (1 << 8) if self.megagroup else 0
        flags |= (1 << 9) if self.restricted else 0
        flags |= (1 << 10) if self.democracy else 0
        flags |= (1 << 11) if self.signatures else 0
        flags |= (1 << 12) if self.min else 0
        flags |= (1 << 13) if self.access_hash else 0
        flags |= (1 << 6) if self.username else 0
        flags |= (1 << 9) if self.restriction_reason else 0
        writer.write_int(flags)

        writer.write_int(self.id)
        if self.access_hash:
            writer.write_long(self.access_hash)

        writer.tgwrite_string(self.title)
        if self.username:
            writer.tgwrite_string(self.username)

        self.photo.on_send(writer)
        writer.tgwrite_date(self.date)
        writer.write_int(self.version)
        if self.restriction_reason:
            writer.tgwrite_string(self.restriction_reason)

    @staticmethod
    def empty():
        """Returns an "empty" instance (all attributes are None)"""
        return Channel(None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)

    def on_response(self, reader):
        flags = reader.read_int()

        if (flags & (1 << 0)) != 0:
            self.creator = True  # Arbitrary not-None value, no need to read since it is a flag

        if (flags & (1 << 1)) != 0:
            self.kicked = True  # Arbitrary not-None value, no need to read since it is a flag

        if (flags & (1 << 2)) != 0:
            self.left = True  # Arbitrary not-None value, no need to read since it is a flag

        if (flags & (1 << 3)) != 0:
            self.editor = True  # Arbitrary not-None value, no need to read since it is a flag

        if (flags & (1 << 4)) != 0:
            self.moderator = True  # Arbitrary not-None value, no need to read since it is a flag

        if (flags & (1 << 5)) != 0:
            self.broadcast = True  # Arbitrary not-None value, no need to read since it is a flag

        if (flags & (1 << 7)) != 0:
            self.verified = True  # Arbitrary not-None value, no need to read since it is a flag

        if (flags & (1 << 8)) != 0:
            self.megagroup = True  # Arbitrary not-None value, no need to read since it is a flag

        if (flags & (1 << 9)) != 0:
            self.restricted = True  # Arbitrary not-None value, no need to read since it is a flag

        if (flags & (1 << 10)) != 0:
            self.democracy = True  # Arbitrary not-None value, no need to read since it is a flag

        if (flags & (1 << 11)) != 0:
            self.signatures = True  # Arbitrary not-None value, no need to read since it is a flag

        if (flags & (1 << 12)) != 0:
            self.min = True  # Arbitrary not-None value, no need to read since it is a flag

        self.id = reader.read_int()
        if (flags & (1 << 13)) != 0:
            self.access_hash = reader.read_long()

        self.title = reader.tgread_string()
        if (flags & (1 << 6)) != 0:
            self.username = reader.tgread_string()

        self.photo = reader.tgread_object()
        self.date = reader.tgread_date()
        self.version = reader.read_int()
        if (flags & (1 << 9)) != 0:
            self.restriction_reason = reader.tgread_string()

    def __repr__(self):
        return 'channel#a14dca52 flags:None creator:flags.0?true kicked:flags.1?true left:flags.2?true editor:flags.3?true moderator:flags.4?true broadcast:flags.5?true verified:flags.7?true megagroup:flags.8?true restricted:flags.9?true democracy:flags.10?true signatures:flags.11?true min:flags.12?true id:int access_hash:flags.13?long title:string username:flags.6?string photo:ChatPhoto date:date version:int restriction_reason:flags.9?string = Chat'

    def __str__(self):
        return '(channel (ID: 0xa14dca52) = (creator={}, kicked={}, left={}, editor={}, moderator={}, broadcast={}, verified={}, megagroup={}, restricted={}, democracy={}, signatures={}, min={}, id={}, access_hash={}, title={}, username={}, photo={}, date={}, version={}, restriction_reason={}))'.format(str(self.creator), str(self.kicked), str(self.left), str(self.editor), str(self.moderator), str(self.broadcast), str(self.verified), str(self.megagroup), str(self.restricted), str(self.democracy), str(self.signatures), str(self.min), str(self.id), str(self.access_hash), str(self.title), str(self.username), str(self.photo), str(self.date), str(self.version), str(self.restriction_reason))
