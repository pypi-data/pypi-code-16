TEMPLATE = """{name} @{handle} id: {user_id} {url}"""


def _serialize_user(item: dict) -> dict:
    return {
        'name': item['name'],
        'handle': item['screen_name'],
        'user_id': item['id'],
        'profile_url': item['statusnet_profile_url']
    }


class User:
    @classmethod
    def from_user_dict(cls, user_dict: dict):
        instance = cls.__new__(cls)
        instance.__init__(**_serialize_user(user_dict))
        return instance

    def __init__(self, user_id: int, name: str, handle: str,
                 profile_url: str) -> None:
        self.user_id = user_id
        self.name = name
        self.handle = handle
        self.profile_url = profile_url

    def __repr__(self) -> str:
        return "User(user_id=%d, name=%s, handle=%s, url=%s)" % (
            self.user_id, self.name, self.handle, self.profile_url
        )

    def __str__(self) -> str:
        return TEMPLATE.format(user_id=self.user_id, name=self.name,
                               handle=self.handle, url=self.profile_url)
