import threading

from .exceptions import APIException
from .helper import stringify
from ..simple import Counter


class RequestsManagerBase:
    def __init__(self):
        self.requests = {}
        self.counter = Counter()

    def response(self, index, data):
        if index in self.requests:
            self.requests[index].result = data
            return self.requests.pop(index)

    def request(self, method, data, send=True):
        index = next(self.counter)
        req = Request(self, {'method': method, 'data': data, 'id': index}, send)
        self.requests[index] = req
        return req

    def reset(self, index=None):
        for req in self.requests:
            req.reset()
        self.requests.clear()
        if index:
            self.counter.reset(index)

    def send(self, data):
        raise NotImplementedError

    def __len__(self):
        return len(self.requests)


class Request:
    def __init__(self, manager, data, send=True):
        self._event = threading.Event()
        self.manager = manager
        self.data = data

        self._result = None
        if send:
            self.send()

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        self._result = value
        self._event.set()

    def send(self):
        self.manager.send(self.data)
        return self

    def wait(self, timeout=30):
        if not self.result:
            self._event.wait(timeout)

        if self.result is None:
            raise TimeoutError('Request is timed out!')
        elif 'error' in self.result.get('data', {}):
            error = self.result['data'].get('error')
            message = self.result['data'].get('message')
            raise APIException(error, message)
        return self.result.get('data', {})

    def reset(self):
        if self._event.is_set():
            self._result = None
            self._event.clear()
        return self


class Serializable:
    parser_aliases = {}

    def __init__(self, **kwargs):
        self.__dict__.update(self._prepare(kwargs))

    @classmethod
    def serialize(cls, **kwargs):
        return cls(**{cls.parser_aliases[k] if k in cls.parser_aliases else k: v for k, v in kwargs.items()})

    def deserialize(self):
        reversed_aliases = {v: k for k, v in self.parser_aliases.items()}
        return {reversed_aliases[k] if k in reversed_aliases else k: v for k, v in self.__dict__.items()}

    def _prepare_field(self, field, value):
        if hasattr(self, 'prepare_' + field):
            return getattr(self, 'prepare_' + field)(value)
        return value

    def _prepare(self, data):
        if 'parser_aliases' in data:
            del data['parser_aliases']
        return {field: self._prepare_field(field, value) for field, value in data.items() if hasattr(self, field)}

    def __str__(self):
        return stringify(self.deserialize())


class SerializableModel(Serializable):
    reference = []

    def __init__(self, model):
        self.__dict__.update(self._prepare(model))

    @classmethod
    def serialize(cls, model):
        return cls(model)

    def _prepare(self, data):
        assert isinstance(data, list) and len(data) == 2, 'Wrong assignment!'
        model_name, obj = data
        assert model_name.split('.') == self.reference, 'Wrong model reference!'
        return super(SerializableModel, self)._prepare(obj)
