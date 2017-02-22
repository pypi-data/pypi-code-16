from oem_framework.format import Format
from oem_framework.plugin import Plugin

import logging

try:
    import json
except ImportError:
    json = None

log = logging.getLogger(__name__)


class JsonFormat(Format, Plugin):
    __key__ = 'json'

    __extension__ = 'json'
    __supports_binary__ = False

    @property
    def available(self):
        return json is not None

    def dump_file(self, obj, fp):
        try:
            json.dump(obj, fp, separators=(',', ':'), sort_keys=True)
            return True
        except Exception as ex:
            log.warn('Unable to dump object to file: %s', ex, exc_info=True)

        return False

    def dump_string(self, obj):
        try:
            return json.dumps(obj, separators=(',', ':'), sort_keys=True)
        except Exception as ex:
            log.warn('Unable to dump object: %s', ex, exc_info=True)

        return None

    def load_file(self, fp):
        try:
            return json.load(fp)
        except Exception as ex:
            log.warn('Unable to load object from file: %s', ex, exc_info=True)

        return None

    def load_string(self, value):
        try:
            return json.loads(value)
        except Exception as ex:
            log.warn('Unable to load object: %s', ex, exc_info=True)

        return None
