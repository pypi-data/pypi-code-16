import os
import pkgutil

from devip.service import Service

SERVICES_DIR = 'services'


def get_service_classes():
    path = os.path.join(os.path.dirname(__file__), SERVICES_DIR)
    modules = pkgutil.iter_modules(path=[path])

    for loader, mod_name, ispkg in modules:
        loaded_mod = __import__('devip.{}.{}'.format(SERVICES_DIR, mod_name), fromlist=[mod_name])

        for key, cls in loaded_mod.__dict__.items():
            if isinstance(cls, type) and issubclass(cls, Service) and cls != Service:
                yield cls


def get_services(*names):
    for cls in get_service_classes():
        if not names or getattr(cls, 'name', None) in names:
            yield cls
