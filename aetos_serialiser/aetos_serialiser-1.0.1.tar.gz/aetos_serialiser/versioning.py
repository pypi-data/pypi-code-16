class Versioning(object):
    def __init__(self, version):
        self.version = version

    def __getattribute__(self, name):
        if name in ['version', '__dict__']:
            return object.__getattribute__(self, name)

        if self.version:
            versioned_method_name = name + '__v%s' % self.version
            try:
                return object.__getattribute__(self, versioned_method_name)
            except AttributeError:
                pass

        return object.__getattribute__(self, name)

    @classmethod
    def _get_class_name(cls):
        return cls.__name__
