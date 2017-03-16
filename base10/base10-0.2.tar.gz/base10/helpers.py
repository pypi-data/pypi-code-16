from base10.base import Metric


class MetricHelper(Metric):
    __initialised__ = False

    def __new__(cls, *args, **kwargs):
        if not cls.__initialised__:
            if 'name' in kwargs:
                cls._name = kwargs.pop('name')
            else:
                if not hasattr(cls, '_name'):
                    raise ValueError('_name is required')

            if 'fields' in kwargs:
                cls._fields = kwargs.pop('fields')
            else:
                if not hasattr(cls, '_fields'):
                    raise ValueError('_fields is required')

            if 'metadata' in kwargs:
                cls._metadata = kwargs.pop('metadata')
            else:
                if not hasattr(cls, '_metadata'):
                    raise ValueError('_metadata is required')

            if 'time' in cls._fields:
                cls._fields.remove('time')

            cls.__initialised__ = True

        return super(Metric, cls).__new__(cls, *args, **kwargs)

    def __init__(self, **kwargs):
        self._verify_and_store(kwargs)


class MetricHandler(object):
    def __init__(self, *args, **kwargs):
        pass

    def read(self):
        while True:
            yield self._dialect.from_string(next(self._transport.read()))

    def write(self, metric):
        return self._transport.write(self._dialect.to_string(metric))
