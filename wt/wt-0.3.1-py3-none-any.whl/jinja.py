# -*- coding: utf-8 -*-

import os

import jinja2
import markdown


class Registry(object):

    def __init__(self):
        self._functions = []

    def add(self, fn):
        self._functions.append(fn)
        return fn

    def __iter__(self):
        for fn in self._functions:
            yield fn


filters = Registry()
functions = Registry()


def get_env(workdir, **config):
    loader = jinja2.ChoiceLoader([
        jinja2.FileSystemLoader(
            os.path.join(workdir, 'templates')),
        jinja2.FileSystemLoader(
            os.path.join(os.path.dirname(__file__), 'templates'))
    ])
    md_exts = config.pop('markdown_extensions', [])
    env = jinja2.Environment(loader=loader, **config)
    env.add_extension('jinja2.ext.autoescape')

    try:
        import jinja_helpers  # noqa
    except ImportError:
        pass

    for fn in filters:
        env.filters[getattr(fn, 'filter_name', fn.__name__)] = fn

    for fn in functions:
        env.globals[getattr(fn, 'function_name', fn.__name__)] = fn

    if 'markdown' not in env.filters:

        def md(text):
            return markdown.markdown(text,
                                     extensions=md_exts,
                                     output_format='html5')

        env.filters['markdown'] = md
    return env
