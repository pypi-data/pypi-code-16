import logging
import sys
from importlib import import_module

from ..app.imports import list_submodules, join
from ..modules.config import AppConfig

BASE_APP_MODULE = 'app'

log = logging.getLogger('NucleusApp')


class AppsRegistry:
    def __init__(self, application, installed_apps=()):
        if installed_apps is None and hasattr(sys.modules[__name__], 'modules'):
            raise RuntimeError("You must supply an installed_apps argument.")

        self.application = application
        self.apps_configs = {}

        self.ready = False

        if installed_apps is not None:
            self.populate(installed_apps)

    def populate(self, installed_apps):
        if self.ready:
            return

        for app_module_name in installed_apps:
            log.debug('Loader: Load "{}"'.format(app_module_name))
            module = import_module(app_module_name)
            submodules = list_submodules(app_module_name, ignore_names=['__init__'])

            if BASE_APP_MODULE not in submodules:
                continue

            base_app_module = import_module(join(app_module_name, BASE_APP_MODULE))
            attr_object = None
            attr = None
            for attribute in dir(base_app_module):
                attr_object = getattr(base_app_module, attribute)
                attr = attribute

                # BUG: error occurred if the attr_object is not a class
                # FIX: check: attr_object is any class
                if not isinstance(attr_object, type):
                    continue

                if issubclass(attr_object, AppConfig) and attr_object is not AppConfig:
                    break
            if attr_object is None:
                log.warning('Loader: Module "{}" is not valid!'.format(app_module_name))
                break
            app_config = attr_object(self.application, app_module_name, module, submodules)
            setattr(base_app_module, attr, app_config)
            if app_config.name in self.apps_configs:
                raise RuntimeError(f"NucleusApp can't run application with duplicate names."
                                   f"\nApp'{app_config.name}' from '{app_module_name}'")
            app_config.setup()
            self.application.middleware.populate_module(app_config)
            log.debug('Loader: Finish loading "{}"'.format(app_module_name))
            self.apps_configs[app_config.name] = app_config
        self.ready = True

    def get_app_config(self, app_name):
        if app_name in self.apps_configs:
            return self.apps_configs[app_name]
        raise RuntimeError(f"Application '{app_name}' is not installed!")
