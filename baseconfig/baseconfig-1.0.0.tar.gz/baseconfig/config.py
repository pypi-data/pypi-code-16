import baseconfig
import json
import platform


class DefaultLoader():
    def load(self, name, chain):
        source = self._load_source(name)
        return DefaultFinder().find(source, chain)

    def _load_source(self, name):
        try:
            with open(name + ".json") as f:
                return json.load(f)
        except FileNotFoundError:
            raise baseconfig.ConfigNotFoundException()


class DefaultFinder():
    def find(self, source, chain):
        return self._find_value_in(source, chain)

    def _find_value_in(self, obj, remaining_chain, processed_chain=[]):
        key = remaining_chain[0]
        try:
            value = obj[key]
        except (KeyError, TypeError):
            error = "The value {key} wasn't found in {path} node.".format(
                key=key,
                path="/".join(processed_chain),
            )
            raise baseconfig.ValueMissingException(error)

        if len(remaining_chain) == 1:
            return value

        return self._find_value_in(
            value, remaining_chain[1:], processed_chain + [key])


class Config:
    def __init__(self, load=DefaultLoader().load, names=None):
        self._load = load
        self._names = names or self._default_names

    def find_value(self, key, validators=[]):
        if isinstance(validators, baseconfig.Validator):
            validators = [validators]

        chain = key.split("/")

        last_ex = None
        for name in self._names:
            try:
                value = self._load(name, chain)
                if validators:
                    self._validate(value, validators)
                return value
            except (baseconfig.ConfigNotFoundException,
                    baseconfig.ValueMissingException) as ex:
                # Raise the exception only if the code reached the last
                # element. Exceptions encountered on all but last elements can
                # simply be ignored, since there is a chance to get the value
                # from the next sources.
                last_ex = ex

        raise last_ex

    def check_all(self):
        members = dir(self)
        for member in members:
            if not member.startswith("_"):
                member_type = getattr(type(self), member)
                if isinstance(member_type, property):
                    try:
                        member_type.__get__(self)
                        yield (member, None)
                    except baseconfig.InvalidValueException as ex:
                        yield (member, ex)

    @property
    def _default_names(self):
        return [
            "config.{machine}".format(machine=platform.node()),
            "config"
        ]

    def _validate(self, value, validators):
        for validator in validators:
            validator.ensure_valid(value)
