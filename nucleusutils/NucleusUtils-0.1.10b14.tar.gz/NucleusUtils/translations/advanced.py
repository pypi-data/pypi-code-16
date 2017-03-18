import inspect
import sys

import jinja2
from jinja2 import Undefined as _Undef

from . import Translator
from .filters import number_ending as _num_ending_filter

UNDEFINED_WORD = '%undefined%'


class AdvancedTranslator(Translator):
    def __init__(self, path=None, default_locale='default', env=None):
        super(AdvancedTranslator, self).__init__(path, default_locale)
        self.jinja_env = jinja2.Environment(cache_size=0, undefined=Undefined)

        self.filters['number'] = _num_ending_filter
        self.globals.update(env or {})

        self.raw_translate = super(AdvancedTranslator, self).translate

    @property
    def globals(self):
        return self.jinja_env.globals

    @property
    def filters(self):
        return self.jinja_env.filters

    def translate(self, word, locale=None, env=None, module=None):
        if env is None:
            env = {}
        if module is None:
            frame = inspect.stack()[1]
            module = inspect.getmodule(frame[0]).__name__
        template = super(AdvancedTranslator, self).translate(word, locale, module)
        return self.render(template, env, locale, module=module)

    t = translate

    def render(self, template, env=None, locale=None, module=None):
        if locale is None:
            locale = self.default_locale
        if env is None:
            env = {}
        env.update({'template': template, 'locale': locale, 'module': module})
        text = ''
        try:
            template = self.jinja_env.from_string(template)
            text = template.render(**env)
        except BaseException as e:
            text = f"Error: {e}\nLocale: {locale}, Module: {module}\nTemplate: {template}"
            self.log.exception(text, exc_info=sys.exc_info())
        return text


class Undefined(_Undef):
    def __int__(self):
        return 0

    def __str__(self):
        return UNDEFINED_WORD

    def __int__(self):
        return 0

    def __float__(self):
        return .0

    def __le__(self, other):
        return False

    def __lt__(self, other):
        return False

    def __gt__(self, other):
        return None

    def __ge__(self, other):
        return None

    def __iter__(self):
        yield from UNDEFINED_WORD

    def __add__(self, other):
        return other

    def __sub__(self, other):
        return other

    def __divmod__(self, other):
        return other

    def __get__(self, instance, owner):
        return UNDEFINED_WORD

    def __getitem__(self, item):
        return UNDEFINED_WORD


translator = AdvancedTranslator()
