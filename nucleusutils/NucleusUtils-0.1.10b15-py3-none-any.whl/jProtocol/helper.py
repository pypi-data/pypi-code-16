import json as _json
from json import JSONEncoder


class EntityEncoder(JSONEncoder):
    def default(self, obj):
        from .entity import Entity
        if isinstance(obj, Entity):
            return clean(obj.to_protocol())
        elif isinstance(obj, (set, tuple)):
            return list(obj)
        return str(obj)


def stringify(data, minimize=True):
    return _json.dumps(data,
                       cls=EntityEncoder,
                       separators=(',', ':') if minimize else (', ', ': '),
                       ensure_ascii=True)


def parse(data):
    return _json.loads(data)


def clean(data):
    if isinstance(data, dict):
        return {k: v for k, v in data.items() if v is not None}
    return data
