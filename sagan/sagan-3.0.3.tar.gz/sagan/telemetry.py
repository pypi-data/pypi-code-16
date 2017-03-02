_FIFO = open('/tmp/sagan_telemetry', 'w')
import json

class Telemetry:

    @staticmethod
    def update(prefix: str, data: str):
        try:
            _FIFO.write("{}:{}\n".format(prefix[0:3], json.dumps(data)))
            _FIFO.flush()
        except:
            return False
        return True
