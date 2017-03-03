try:
    import ConfigParser
except:
    import configparser as ConfigParser


class ConfigParserBackend(object):
    def __init__(self, path, section):
        self.config = config = ConfigParser.RawConfigParser()
        self.config.read(path)
        self.section = section

    def get(self, key):
        try:
            return self.config.get(self.section, key)
        except ConfigParser.NoOptionError as ex:
            raise AttributeError("Key %s not in section %s" % (key,
                                                               self.section))
