TEMPLATE = """{name} !{handle} id: {group_id} {url}"""


def _serialize_group(item: dict) -> dict:
    return {
        'name': item['fullname'],
        'handle': item['nickname'],
        'group_id': item['id'],
        'profile_url': item['url']
    }


class Group:
    @classmethod
    def from_group_dict(cls, group_dict: dict):
        instance = cls.__new__(cls)
        instance.__init__(**_serialize_group(group_dict))
        return instance

    def __init__(self, group_id: int, name: str, handle: str,
                 profile_url: str) -> None:
        self.group_id = group_id
        self.name = name
        self.handle = handle
        self.profile_url = profile_url

    def __repr__(self) -> str:
        return "group(group_id=%d, name=%s, handle=%s, url=%s)" % (
            self.group_id, self.name, self.handle, self.profile_url
        )

    def __str__(self) -> str:
        return TEMPLATE.format(group_id=self.group_id, name=self.name,
                               handle=self.handle, url=self.profile_url)
