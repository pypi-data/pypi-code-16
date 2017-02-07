import hashlib
import pickle

from groundwork.patterns import GwBasePattern
from groundwork.util import gw_get


class GwValidatorsPattern(GwBasePattern):

    def __init__(self, app, **kwargs):
        super(GwValidatorsPattern, self).__init__(app, **kwargs)
        self.app = app
        self.validators = ValidatorsPlugin(self)
        if not hasattr(self.app, "validators"):
            self.app.validators = ValidatorsApplication(self)


class ValidatorsPlugin:

    def __init__(self, plugin):
        self.plugin = plugin
        self.app = plugin.app

    def register(self, name, description, algorithm=hashlib.sha256, attributes=None):
        return self.app.validators.register(name, description, self.plugin, algorithm=algorithm, attributes=attributes)

    def unregister(self, name):
        self.app.validators.unregister(name)

    def get(self, name):
        self.app.validators.get(name, self.plugin)


class ValidatorsApplication:

    def __init__(self, app):
        self.app = app
        self._validators = {}

    def register(self, name, description, plugin, algorithm=hashlib.sha256, attributes=None):
        if name in self._validators.keys():
            raise KeyError("Validator %s already registered" % name)

        self._validators[name] = Validator(name, description,
                                           algorithm=algorithm,
                                           attributes=attributes,
                                           plugin=plugin)

        return self._validators[name]

    def unregister(self, name):
        if name in self._validators.keys():
            del(self._validators[name])
        else:
            raise KeyError("Validator %s does not exist" % name)

    def get(self, name, plugin):
        gw_get(self._validators, name, plugin)


class Validator:

    def __init__(self, name, description, algorithm=hashlib.sha256, attributes=None, plugin=None):
        self.name = name
        self.description = description
        self.plugin = plugin
        self.algorithm = algorithm
        self.attributes = attributes

    def validate(self, data, hash_string):
        if self.hash(data) == hash_string:
            return True
        return False

    def hash(self, data, return_hash_object=False, strict=False):
        current_hash = self.algorithm()
        if self.attributes is None:
            current_hash.update(pickle.dumps(data))
        else:
            for attribute in self.attributes:
                if strict and hasattr(data, attribute) is False:
                    raise AttributeError("Data has no attribute called %s" % attribute)
                current_hash.update(pickle.dumps(getattr(data, attribute, None)))

        if return_hash_object:
            return current_hash
        return current_hash.hexdigest()
