import inspect
import json
import logging
import os


class Translator:
    def __init__(self, path=None, default_locale='default'):
        self.log = logging.getLogger('translations')

        if path is None:
            path = os.path.join(os.path.dirname(__import__('__main__').__file__), 'locales')

        self.path = path
        self.default_locale = default_locale

        self.__translations = {}

    @property
    def translations(self):
        return self.__translations

    def translate(self, word, locale=None, module=None):
        if locale is None:
            locale = self.default_locale
        if module is None:
            frame = inspect.stack()[1]
            module = inspect.getmodule(frame[0]).__name__
        return self.get_translation(word, locale, module) or word

    def get_translation(self, word, locale, module):
        if locale is None:
            locale = self.default_locale
        path = module_to_path(module)
        if not os.path.isdir(path):
            self._create_dir(path)

        if module not in self.__translations:
            self.__translations[module] = {}
        if locale not in self.__translations[module]:
            locale_data = self._read_locale(path, locale)
            self.__translations[module][locale] = locale_data

        if word not in self.__translations[module][locale]:
            self.log.warning('Word "{}" is not found in {}::{}'.format(word, module, locale))
            self.__translations[module][locale][word] = None
            self._write_locale(path, locale)

        return self.__translations[module][locale][word]

    def _read_locale(self, path, locale):
        full_path = os.path.join(self.path, path, locale + '.json')
        if not os.path.isfile(full_path):
            data = {}
            self._write_locale(path, locale, data)
        else:
            self.log.debug('Read file: "{}"'.format(full_path))
            with open(full_path, 'r') as file:
                data = json.load(file)
        return data

    def _write_locale(self, path, locale, data=None):
        full_path = os.path.join(self.path, path, locale + '.json')
        module = path_to_module(path)
        data = data or self.__translations.get(module, {}).get(locale, {})
        if not len(data):
            return False
        with open(full_path, 'w+') as file:
            self.log.debug('Write file: "{}"'.format(full_path))
            json.dump(data, file,
                      ensure_ascii=False, indent=2, sort_keys=True)

    def _create_dir(self, path):
        full_path = os.path.join(self.path, path)
        if os.path.isfile(full_path):
            full_path = os.path.split(full_path)[0]
        if not os.path.isdir(full_path):
            self.log.debug('Create dir: "{}"'.format(full_path))
            os.makedirs(full_path, exist_ok=True)
        return full_path

    def add_keys(self, keys, module=None, locale=None):
        assert isinstance(keys, (list, dict)), 'keys must be list'

        if module is None:
            frame = inspect.stack()[1]
            module = inspect.getmodule(frame[0]).__name__
        if locale is None:
            locale = self.default_locale

        full_path = module_to_path(module)
        self._create_dir(full_path)

        if module not in self.__translations:
            self.__translations[module] = {}
        if locale not in self.__translations[module]:
            self.__translations[module][locale] = {}

        self.__translations[module][locale] = self._read_locale(full_path, locale)

        if isinstance(keys, list):
            for item in keys:
                if item not in self.__translations[module][locale]:
                    self.__translations[module][locale][item] = None
        else:
            self.__translations[module][locale].update(keys)
        self._create_dir(full_path)
        self._write_locale(full_path, locale)


def path_to_module(path):
    return '.'.join(path.split(os.sep))


def module_to_path(module):
    return os.path.join(*module.split('.'))


translator = Translator()
