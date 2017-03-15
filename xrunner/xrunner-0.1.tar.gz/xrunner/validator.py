from comparator import Comparator
from settings import COMPARATOR_NICK_LIST

import logging
log = logging.getLogger("XMLTestLogger")


class Validator:

    def __init__(self):
        log.info("Initializing Validator")

    def validate(self):
        raise NotImplementedError("Abstract Validator requires validate() \
                                  method implemented")

    @classmethod
    def new_validator(self, nick, property):
        return CompareValidator(property)


class CompareValidator(Validator):

    def __init__(self, data):
        self.nick = 'compare'
        log.debug(" COMPAREVALIDATOR: " + str(data))
        # Extract data from validator_value
        for k, val in data.iteritems():
            if 'expected' in k:
                self.expected = val
                continue

            if 'comparator' in k:
                self.condition = val
                continue

            # Load the Comparator
            if k in COMPARATOR_NICK_LIST:
                self.comparator = Comparator.new_comparator(k, val, data)

    def to_string(self):
        return self.nick + ' ' + self.comparator.to_string()

    def validate(self, response_content):
        return self.comparator.compare(response_content)
