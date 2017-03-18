import copy
import json
import os

from . import path_to_module, Translator


def strip_path(full, remove):
    if full.startswith(remove):
        return full[len(remove):].lstrip(os.sep)
    return full


def sort(data):
    return dict(sorted(data.items(), key=lambda item: item[0]))


def detect_locales(path):
    result = []

    for root, dirs, files in os.walk(path):
        for filename in files:
            name, _, ext = filename.rpartition('.')
            if ext != 'json':
                raise RuntimeError('Wrong locales dir! This dir contains \'{}\''.format(os.path.join(root, filename)))
            if ext == 'json' and name and name not in result:
                result.append(name)
                yield name


def tree(path, lang=None):
    result = {}

    def _filter(name):
        if lang:
            return name == lang + '.json'
        else:
            return name.endswith('.json')

    for root, dirs, files in os.walk(path):
        module = path_to_module(strip_path(root, path)) or '*'
        if module not in result:
            result[module] = {}

        for filename in files:
            if not _filter(filename):
                continue
            with open(os.path.join(root, filename), 'r') as file:
                if lang:
                    obj = json.load(file)
                else:
                    obj = {k: None for k in json.load(file).keys()}
                result[module].update(sort(obj))

        if not len(result[module]):
            del result[module]

    return sort(result)


def load(path):
    result = {}
    data_tree = tree(path)
    for locale in detect_locales(path):
        data = copy.deepcopy(data_tree)

        translates = tree(path, locale)
        for module, translate in translates.items():
            data[module].update(translate)
        result[locale] = data
    return sort(result)


def dump(data, out):
    translator = Translator(out)
    for locale, locale_obj in data.items():
        for module, module_obj in locale_obj.items():
            translator.add_keys(module_obj, module if module != '*' else '__main__', locale)
    return translator


if __name__ == '__main__':
    PATH = os.path.abspath('../locales')
    OUT_PATH = os.path.abspath('../out')
    dump(load(PATH), OUT_PATH)
