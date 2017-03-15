from validator import Validator
from settings import VALIDATOR_NICK_LIST
from dial import Dialer

import logging
log = logging.getLogger("XMLTestLogger")


class AbstractTest:

    def run(self):
        raise NotImplementedError("Test Should implement run() method")


class Test(AbstractTest):

    def __init__(self, test_data, url_prefix="http://search.unbxdapi.com"):
        # Load all the properties of test
        # Must Properties
        self.name = self.url = self.group = self.validators = None
        self.method = 'GET'

        for prop in test_data:
            if 'name' in prop:
                self.name = prop['name']
            if 'url' in prop:
                self.url = prop['url']
            if 'group' in prop:
                self.group = prop['group']
            if 'validators' in prop:
                _validators_ = prop['validators']
            if 'method' in prop:
                self.method = prop['method']

            if 'request' in prop:
                self.request_property = prop['request']
            else:
                self.request_property = {}

        log.debug(
            "\nTest Properties Loaded: " +
            "\n NAME: " +
            self.name +
            "\n URL: " +
            self.url +
            "\n GROUP: " +
            self.group +
            "\n METHOD: " +
            self.method)
        log.debug(" VALIDATORS: " + str(_validators_))

        if self.name is None or self.url is None\
                or self.group is None:
            log.error(self.name)
            raise Exception("Missing property for test case.")

        self.validators = self.__get_validators__(_validators_)

        if 'http' not in self.url:
            self.url = url_prefix + self.url

        self.dialer = self.__get_dialer__(
            self.url,
            self.method,
            self.request_property)

    def to_string(self):
        retr = self.name + " " + self.url + " " + self.group + " " + self.method
        for validator in self.validators:
            retr = retr + " " + validator.to_string()
        return retr

    def __get_dialer__(self, url, method, request_property):
        return Dialer(url, method, request_property)

    def __get_validators__(self, _validators_):
        validators = []
        for validator in _validators_:
            for k, val in validator.iteritems():
                if k in VALIDATOR_NICK_LIST:
                    validators.append(Validator.new_validator(k, val))
        return validators

    def run(self):
        # Check if there are any validators
        if len(self.validators) <= 0:
            raise Exception("There are no validators for test case")
        response = self.dialer.dial()
        for validator in self.validators:
            if not validator.validate(response):
                raise Exception("Failed: " + self.name + " for validator \n\t" +
                                validator.to_string())
                return False
        return True
