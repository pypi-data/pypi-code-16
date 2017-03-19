import json
from json import JSONEncoder


class ProtoEncoder(JSONEncoder):
    def default(self, obj):
        try:
            return JSONEncoder.default(self, obj)
        except:
            return str(obj)


def stringify(data):
    return json.dumps(data,
                      cls=ProtoEncoder,
                      separators=(',', ':'),
                      ensure_ascii=True)
