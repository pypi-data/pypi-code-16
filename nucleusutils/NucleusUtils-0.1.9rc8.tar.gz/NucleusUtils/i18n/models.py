import json

from NucleusUtils.i18n import defaults


class Locale:
    def __init__(self, title, content=None):
        if content is None:
            content = {}
        self.name = title
        self._data = content

    def update(self, data):
        assert isinstance(data, dict)
        self._data.update(data)

    def get_translation(self, key):
        return self[key]

    def __getitem__(self, item):
        return self._data.get(item, None)

    def __str__(self):
        return json.dumps(self._data)

    def __repr__(self):
        return '<Locale "' + self.name + '">'


class Context:
    def __init__(self, name=defaults.CONTEXT_NAME):
        self.name = name
        self.locales = []

    def get_locale(self, name, create=False):
        locale = self[name]
        if locale:
            return locale

        if create:
            locale = Locale(name)
            self.locales.append(locale)
            return locale

        return None

    def get_locales(self):
        return [locale.name for locale in self.locales]

    def __getitem__(self, item):
        for locale in self.locales:
            if locale.name == item:
                return locale
        return None

    def __str__(self):
        return json.dumps(self.locales)

    def __repr__(self):
        return '<Context "' + self.name + '" with locales: ["' + ', '.join(
            [locale.title for locale in self.locales]) + '"]>'


class ContextProcessor:
    def __init__(self):
        self.contexts = [Context(defaults.CONTEXT_NAME)]

    def get_context(self, name=defaults.CONTEXT_NAME, create=False):
        for context in self.contexts:
            if context.name == name:
                return context

        if create:
            context = Context(name)
            self.contexts.append(context)
            return context
        return None

    def get_contexts(self):
        return [context.name for context in self.contexts]

    def get_locales(self):
        locales = []
        for context in self.contexts:
            for locale in context.get_locales():
                if locale not in locales:
                    locales.append(locale)
        return locales
