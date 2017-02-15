import os

import dj_database_url


class ConfigField(object):
    def __init__(self, help='', default=None, dev_default=None):
        self.help = help
        self._default = default
        self._dev_default = dev_default or default
        self.id = None
        self.group = None
        self.env_prefix = ''
        self.config = None

    def init(self, env_prefix, group, id, config):
        self.env_prefix = env_prefix
        self.id = id
        self.group = group
        self.config = config

    @property
    def default(self):
        return self._default() if callable(self._default) else self._default

    @property
    def dev_default(self):
        return self._dev_default() if callable(self._dev_default) else self._dev_default or self.default

    def _convert(self, value):
        """This method should be overloaded in other types. value is always string
        (can come from either config file or environmental variable)

        :param value:
        :type value: str
        :return: Object
        :rtype: object
        """
        return value

    @property
    def env_variable(self):
        return ((self.env_prefix.upper() + '_') if self.env_prefix else '') + self.group.upper() + '_' + self.id.upper()

    def get(self):
        var = self._convert(os.environ.get(self.env_variable) or self.config.get(self.group, self.id))
        if var is None:
            print('[WARNING] (this is ok during config generation) No %s.%s in config file, '
                  'make sure that env variable %s was set to app config, and '
                  'it has all required fields defined, using default: %s' % (self.group, self.id,
                                                                             (self.env_prefix + '_' if self.env_prefix else '') + 'CONFIG',
                                                                             self.default))
            return self.default
        return var


class Url(ConfigField):
    """For now it's the same as default (String), in the future may be extended

    """
    pass


class Integer(ConfigField):
    def _convert(self, value):
        return int(value)


class Float(ConfigField):
    def _convert(self, value):
        return float(value)


class String(ConfigField):
    """For now it's the same as default (String), in the future may be extended

        """
    pass


class Database(ConfigField):
    def get(self):
        db_url = super(Database, self).get()
        return dj_database_url.parse(db_url, conn_max_age=600)


class Boolean(ConfigField):
    def _convert(self, value):
        if isinstance(value, Boolean):
            return value

        if isinstance(value, str):
            if value.lower() in ('true', '1'):
                return True
            elif value.lower() in ('false', 0):
                return False
            raise ValueError('%s is not a proper boolean' % value)

        return value is not None


class Path(ConfigField):
    def __init__(self, help='', default=None, dev_default=None, root='/', dev_root=None):
        super(Path, self).__init__(help, default, dev_default)
        self.root = root
        self.dev_root = dev_root

    @property
    def dev_default(self):
        path = super(Path, self).dev_default
        print 'get default %s' % path
        if not os.path.isabs(path):
            return os.path.join(self.dev_root, path)
        return path

    @property
    def default(self):
        path = super(Path, self).default
        if not os.path.isabs(path):
            return os.path.join(self.root, path)
        return path

