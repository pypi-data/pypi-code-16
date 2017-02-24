import logging
import sys

import jinja2

from NucleusUtils.i18n.defaults import Undefined
from NucleusUtils.i18n.filters import do_translate as _translate_filter
from NucleusUtils.i18n.filters import number_ending as _num_ending_filter
from . import defaults
from .locales import get_locale

log = logging.getLogger(defaults.LOGGER_NAME)

default_locale = ['']
jinja_env = jinja2.Environment(cache_size=0, undefined=Undefined)

jinja_env.filters['number'] = _num_ending_filter
jinja_env.filters['translate'] = _translate_filter


def set_default_locale(name=default_locale):
    default_locale[0] = name


def get_default_locale():
    return default_locale[0]


def raw_translate(key, locale=None, context=defaults.CONTEXT_NAME):
    if locale is None:
        locale = get_default_locale()
    locale = get_locale(locale, context)
    if locale:
        result = locale.get_translation(key)
        if result is not None:
            return result
        if locale.name != get_default_locale():
            log.warning(f"Translate for '{key}' is missing in locale '{locale.name}' with context '{context}'")
            return raw_translate(key, get_default_locale(), context)
    else:
        log.error(f"Locale {locale} is missing!")
        raise KeyError(locale)
    log.warning(f"Translate for '{key}' is missing in locale '{locale.name}' with context '{context}'")
    return key


def translate(key, locale=None, context=defaults.CONTEXT_NAME, parse=True, env=None):
    if isinstance(key, LazyTranslate):
        return key.translate(locale, context, parse, env)
    if env is None:
        env = {}
    if locale is None:
        locale = get_default_locale()
    text = raw_translate(key, locale, context)

    if parse:
        text = render(text, env, locale, context)

    return text


def render(template, env=None, locale=None, context=defaults.CONTEXT_NAME):
    if locale is None:
        locale = get_default_locale()
    if env is None:
        env = {}
    env.update({'template': template, 'locale': locale, 'context': context})
    text = ''
    try:
        template = jinja_env.from_string(template)
        text = template.render(**env)
    except BaseException as e:
        text = f"[{defaults.LOGGER_NAME}] Error: {e}\nLocale: {locale}, Context: {context}\nTemplate: {text}"
        log.exception(text, exc_info=sys.exc_info())
    return text


class LazyTranslate:
    def __init__(self, text, context=None):
        assert isinstance(text, str)
        self.text = text
        self.context = context

    def translate(self, locale, context=defaults.CONTEXT_NAME, parse=None, env=None):
        if env is None:
            env = {}
        return translate(self.text, locale=locale, context=self.context or context, parse=parse, env=env)

    def __str__(self):
        return f"LazyTranslate('{self.text}', context='{self.context or '$' + defaults.CONTEXT_NAME}')"
