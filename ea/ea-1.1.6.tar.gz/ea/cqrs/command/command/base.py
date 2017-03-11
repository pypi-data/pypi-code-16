import six

from ea.lib.datastructures import ImmutableDTO
from ea.cqrs.command.command.meta import CommandMeta


class Command(six.with_metaclass(CommandMeta)):

    @property
    def errors(self):
        return ImmutableDTO(self._errors)

    @property
    def params(self):
        return ImmutableDTO(self._params)

    def __init__(self, **params):
        self._params, self._errors = self.meta.load(params)

    def dump(self):
        if not self.is_valid():
            raise ValueError("Cannot dump command in invalid state.")
        return ImmutableDTO(self.meta.schema.dump(self._params)[0])

    def is_valid(self):
        return not bool(self._errors)

    def __serialize__(self, func):
        return func(self.dump())

    def __repr__(self):
        args = []
        for name in self.meta.get_field_names():
            args.append("%s=%s" % (name, repr(self._params.get(name))))
        return "%s(%s)" % (type(self).__name__, ', '.join(args))
