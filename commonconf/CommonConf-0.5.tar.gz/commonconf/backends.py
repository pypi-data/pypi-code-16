from commonconf.proxy import ConfProxy
from importlib import import_module


def use_configuration_backend(module, args=[]):
    module, attr = module.rsplit('.', 1)
    mod = import_module(module)
    config_module = getattr(mod, attr)

    ConfProxy.backend = config_module(*args)


def use_django_backend():
    use_configuration_backend('commonconf.backend.django.DjangoSettings')


def use_configparser_backend(path, section):
    use_configuration_backend('commonconf.backend.parser.ConfigParserBackend',
                              [path, section])
