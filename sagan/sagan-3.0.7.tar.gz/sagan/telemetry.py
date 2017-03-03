import os
import json

_FIFO = None
if os.environ.get('TELEMETRY', '0') == '1':
    _FIFO = open('/tmp/sagan_telemetry', 'w')


class Telemetry:

    @staticmethod
    def update(prefix: str, data: str):
        try:
            if os.environ.get('TELEMETRY', '0') == '1':
                _FIFO.write("{}:{}\n".format(prefix[0:3], json.dumps(data)))
                _FIFO.flush()
        except:
            return False
        return True
