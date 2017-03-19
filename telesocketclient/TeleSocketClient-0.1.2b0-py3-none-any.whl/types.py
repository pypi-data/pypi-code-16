from NucleusUtils.jProtocol.client import Serializable, SerializableModel


class APIException(Serializable):
    error = 'APIException'
    message = 'exception'
    data = {}


class User(SerializableModel):
    reference = ['User']

    id = None
    username = None
    last_login = None
    token = None


class Session(SerializableModel):
    reference = ['Session']

    id = None
    user = None


class WebHook(Serializable):
    url = ''


class Client(SerializableModel):
    cid = None
    server = None
    user = None
    bot = None

    def prepare_user(self, value):
        if value is None:
            value = {}
        if isinstance(value, User):
            return value
        return User.serialize(**value)
