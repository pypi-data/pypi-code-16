from __future__ import absolute_import


class KafkaRestError(Exception):
    error_code = None

    def __init__(self, error_code, message):
        self.error_code = error_code
        self.message = message

    def __str__(self):
        return " [ERROR CODE] %s [ERROR] %s\n" % (self.error_code, str(self.message))
