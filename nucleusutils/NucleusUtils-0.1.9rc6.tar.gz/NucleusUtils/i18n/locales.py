import json
import logging
import os

from . import defaults
from .models import ContextProcessor, Context, Locale

log = logging.getLogger(defaults.LOGGER_NAME)

context_processor = ContextProcessor()


def get_context(name=defaults.CONTEXT_NAME, generate=False) -> Context:
    return context_processor.get_context(name, generate)


def get_locale(name, context=defaults.CONTEXT_NAME) -> Locale:
    context = get_context(context)
    if context:
        return context.get_locale(name)
    return get_context(defaults.CONTEXT_NAME).get_locale(name)


def load_from_file(filename, context=defaults.CONTEXT_NAME):
    assert isinstance(filename, str)
    filename = os.path.abspath(filename)
    log.debug(f"Load locale from file: '{filename}' ({context})")

    if not os.path.isfile(filename):
        raise FileNotFoundError(filename)

    locale = os.path.split(filename)[-1]
    if locale.endswith('.json'):
        locale = locale[:-5]

    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
        assert isinstance(data, dict)

    get_context(context, True).get_locale(locale, True).update(data)


def load_from_path(path, context=defaults.CONTEXT_NAME):
    assert isinstance(path, str)
    path = os.path.abspath(path)

    log.debug(f"Load locale from directory: '{path}' ({context})")
    if not os.path.isdir(path):
        raise FileNotFoundError(path)

    for file in os.listdir(path):
        try:
            load_from_file(os.path.join(path, file), context=context)
        except:
            continue
