from oem_framework.plugin import Plugin
from oem_format_json.main import JsonFormat

import json
import logging

log = logging.getLogger(__name__)


class JsonPrettyFormat(JsonFormat, Plugin):
    __key__ = 'json/pretty'

    __extension__ = 'pre.json'

    def dump_file(self, obj, fp):
        try:
            json.dump(obj, fp, sort_keys=True, indent=4, separators=(',', ': '))
            return True
        except Exception as ex:
            log.warn('Unable to dump object to file: %s', ex, exc_info=True)

        return False

    def dump_string(self, obj):
        try:
            return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))
        except Exception as ex:
            log.warn('Unable to dump object: %s', ex, exc_info=True)

        return None
