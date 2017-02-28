from .i18n import _, ngettext, translate_created_at
TEMPLATE = """{author_name} @{author_handle}{reply_block} {created_at}
id: {status_id}{detailed_block}
{content}
"""
DETAILED = _(""" conversation id: {conversation_id}
{repeat_block}
{fave_block}
Posted from: {source}
URL: {url}""")


def _serialize_status(item: dict) -> dict:
    if 'retweeted_status' in item:
        item = item['retweeted_status']
    return {
        'status_id': int(item['id']),
        'content': item['text'],
        'author_name': item['user']['name'],
        'author_handle': item['user']['screen_name'],
        'created_at': translate_created_at(item['created_at']),
        'conversation_id': item.get('statusnet_conversation_id'),
        'in_reply_to_status_id': item.get('in_reply_to_status_id'),
        'in_reply_to_screen_name': item.get('in_reply_to_screen_name'),
        'fave_num': item['fave_num'],
        'favorited': item['favorited'],
        'source': item['source'],
        'repeated': item['repeated'],
        'repeat_num': item['repeat_num'],
        'url': item['external_url']
    }


class Status:
    @classmethod
    def from_status_dict(cls, status_dict: dict):
        instance = cls.__new__(cls)
        instance.__init__(**_serialize_status(status_dict))
        return instance

    def __init__(
            self, status_id: int, content: str, author_name: str,
            author_handle: str, created_at: str, fave_num: int, url: str,
            favorited: bool, source: str, repeated: bool, repeat_num: int,
            conversation_id: int=None, in_reply_to_status_id: str=None,
            in_reply_to_screen_name: str=None
    ) -> None:
        self.status_id = status_id
        self.content = content
        self.author_name = author_name
        self.author_handle = author_handle
        self.created_at = created_at
        self.in_reply_to_status_id = in_reply_to_status_id
        self.in_reply_to_screen_name = in_reply_to_screen_name
        self.conversation_id = conversation_id
        self.fave_num = fave_num
        self.favorited = favorited
        self.source = source
        self.repeated = repeated
        self.repeat_num = repeat_num
        self.url = url

    def __repr__(self) -> str:
        template = ('Status(status_id=%d, content="%s", ' +
                    'author_name="%s", author_handle="%s", ' +
                    'created_at="%s"')
        template %= (self.status_id, self.content, self.author_name,
                     self.author_handle, self.created_at)
        if self.conversation_id:
            template += ', conversation_id=%d' % self.conversation_id
        if self.in_reply_to_status_id and self.in_reply_to_screen_name:
            template += ((', in_reply_to_status_id=%s,' +
                          ' in_reply_to_screen_name=%s') %
                         (self.in_reply_to_status_id,
                          self.in_reply_to_screen_name))
        return template + ')'

    def __format_repeat_block(self):
        if self.repeat_num == 0:
            return _('Has not been repeated')
        else:
            if self.repeated:
                you = _('has been repeated by you')
            else:
                you = _('has not been repeated by you')
            return ngettext(
                'Has been repeated by {repeat_num} person ({you})',
                'Has been repeated by {repeat_num} people ({you})',
                self.repeat_num
            ).format(repeat_num=self.repeat_num, you=you)

    def __format_fave_block(self):
        if self.fave_num == 0:
            return _('Has not been favorited')
        else:
            if self.favorited:
                you = _('has been favorited by you')
            else:
                you = _('has not been favorited by you')
            return ngettext(
                'Has been favorited by {fave_num} person ({you})',
                'Has been favorited by {fave_num} people ({you})',
                self.fave_num
            ).format(fave_num=self.fave_num, you=you)

    def __to_str(self, detailed=False):
        reply_block = ''
        if self.in_reply_to_screen_name and self.in_reply_to_status_id:
            reply_block = ' > @%s (id: %s)' % (self.in_reply_to_screen_name,
                                               self.in_reply_to_status_id)
        detailed_block = ''
        if detailed:
            detailed_block = DETAILED.format(
                conversation_id=self.conversation_id, source=self.source,
                fave_block=self.__format_fave_block(), url=self.url,
                repeat_block=self.__format_repeat_block()
            )
        return TEMPLATE.format(
            author_name=self.author_name, author_handle=self.author_handle,
            created_at=self.created_at, status_id=self.status_id,
            content=self.content, reply_block=reply_block,
            detailed_block=detailed_block
        )

    def __str__(self) -> str:
        return self.__to_str()

    @property
    def detailed(self) -> str:
        return self.__to_str(True)
