class ChatActions:
    TYPING = 'typing'
    UPLOAD_PHOTO = 'upload_photo'
    RECORD_VIDEO = 'record_video'
    UPLOAD_VIDEO = 'upload_video'
    RECORD_AUDIO = 'record_audio'
    UPLOAD_AUDIO = 'upload_audio'
    UPLOAD_DOCUMENT = 'upload_document'
    FIND_LOCATION = 'find_location'


class ChatType:
    PRIVATE = "private"
    GROUP = "group"
    SUPER_GROUP = "supergroup"
    CHANNEL = "channel"


class ParseMode:
    MARKDOWN = 'markdown'
    HTML = 'html'


class ChatRole:
    CREATOR = 'creator'
    ADMINISTRATOR = 'administrator'
    MEMBER = 'member'
    LEFT = 'left'
    KICKED = 'kicked'

    @classmethod
    def is_admin(cls, role):
        return role in [cls.ADMINISTRATOR, cls.CREATOR]

    @classmethod
    def is_member(cls, role):
        return role in [cls.MEMBER, cls.ADMINISTRATOR, cls.CREATOR]


class EntityType:
    MENTION = 'mention'  # @username
    HASHTAG = 'hashtag'
    BOT_COMMAND = 'bot_command'
    URL = 'url'
    EMAIL = 'email'
    BOLD = 'bold'  # bold text
    ITALIC = 'italic'  # italic text
    CODE = 'code'  # monowidth string
    PRE = 'pre'  # monowidth block
    TEXT_LINK = 'text_link'  # for clickable text URLs
    TEXT_MENTION = 'text_mention'  # for users without usernames


class ContentType:
    TEXT = 'text'
    AUDIO = 'audio'
    DOCUMENT = 'document'
    GAME = 'game'
    PHOTO = 'photo'
    STICKER = 'sticker'
    VIDEO = 'video'
    VOICE = 'voice'
    NEW_CHAT_MEMBER = 'new_chat_member'
    LEFT_CHAT_MEMBER = 'left_chat_member'
