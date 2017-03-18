from importlib import import_module


class SettingsManager:
    def __init__(self):
        self.settings = {}
        self.settings_module_name = ''

        self.ready_to_load = self.ready = False

    def setup(self, module):
        self.settings_module_name = module

    def load_global_settings(self):
        if self.ready:
            raise RuntimeError('Global settings is already loaded!')

        globals_settings = import_module(__package__ + '.global_settings')
        for attr in dir(globals_settings):
            if attr.isupper():
                self.settings[attr] = getattr(globals_settings, attr)

        self.ready_to_load = True

    def load_settings(self):
        if not self.ready_to_load:
            raise RuntimeError('SettingsManager is not ready to load settings!')

        settings_module = import_module(self.settings_module_name)
        for attr in dir(settings_module):
            if attr.isupper():
                self.settings[attr] = getattr(settings_module, attr)

        self.ready = True

    def load(self, module):
        self.setup(module)
        self.load_global_settings()
        self.load_settings()
        return self

    def get(self, item, default=None):
        if not self.ready:
            raise RuntimeError('SettingsManager is not ready to loading settings!')
        return self.settings.get(item, default)

    def __getitem__(self, item):
        if not self.ready:
            raise RuntimeError('SettingsManager is not ready to loading settings!')
        return self.settings[item]
