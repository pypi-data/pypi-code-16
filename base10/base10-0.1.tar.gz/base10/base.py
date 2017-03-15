from datetime import datetime
from abc import ABCMeta, abstractmethod


class Metric(object):
    def __init__(self, name, fields, metadata, **kwargs):
        self._name = name
        self._fields = fields
        self._metadata = metadata

        if 'time' in self._fields:
            self._fields.remove('time')

        self._verify_and_store(kwargs)

    def _verify_and_store(self, values):
        timestamp = values.pop('time', self._current_timestamp())

        if sorted(self._fields + self._metadata) != sorted(values.keys()):
            raise NameError('Expected {} but got {}'.format(
                sorted(self._fields + self._metadata),
                sorted(values.keys())
                ))

        self._values = values
        self._values['time'] = timestamp

    def _current_timestamp(self):
        return datetime.utcnow()

    @property
    def name(self):
        return self._name

    @property
    def fields(self):
        return self._fields

    @property
    def metadata(self):
        return self._metadata

    @property
    def values(self):
        return self._values

    def __repr__(self):
        return '<Metric:"{}" Fields:{} Metadata:{} Values:{}>'.format(
                self.name,
                self.fields,
                self.metadata,
                self.values)


class Dialect(object):
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def from_string(self, string):
        pass

    @abstractmethod
    def to_string(self, metric):
        pass


class Transport(object):
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def write(self, string):
        pass
