# -*- coding: utf-8 -*-

import os
import logging

from string import Template

import yaml

from .decorators import reloadable


logger = logging.getLogger('wt.base')


@reloadable('(re)loading nested configuration...')
def load_yaml(filename):
    with open(filename, encoding='utf-8') as f:
        data = list(yaml.load_all(f))
    return data[0] if len(data) == 1 else data


def transform(value):
    conv = {
        list: process_list,
        dict: dict_to_object,
        str: lambda x: process_str_file(process_str_env(x)),
    }
    return conv.get(type(value), lambda x: x)(value)


def dict_to_object(obj):
    return Object(**obj)


def process_list(obj):
    return [isinstance(x, dict) and Object(**x) or x for x in obj]


def process_str_env(value):
    return Template(value).safe_substitute(**os.environ)


def process_str_file(value):
    if value[:6] == '{file}':
        workdir = os.environ.get('WT_WORKDIR', '')
        v = load_yaml(os.path.join(workdir, value[6:]))
        return transform(v)
    return value


class Object(object):

    __slots__ = ('_kwargs', )

    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def __getattr__(self, name):
        return transform(self._kwargs.get(name))


class Config(Object):

    def __getattr__(self, name):
        if name in ('paginate', 'jinja'):
            return self._kwargs.get(name, {})
        return super().__getattr__(name)


class Content(Object):

    content_dirname = 'content'
    data_dirname = None

    @classmethod
    def from_dict(cls, workdir, data):
        if isinstance(data, dict):
            data = dict_to_object(data)
        assert isinstance(data, Object)
        p = cls(**data._kwargs)
        if p.src and not os.path.isabs(p.src):
            p.src = os.path.join(workdir,
                                 cls.content_dirname,
                                 cls.data_dirname or '',
                                 p.src)
        return p

    @property
    def text(self):
        t = ''
        if self.src and os.path.isfile(self.src):
            with open(self.src, 'rt', encoding='utf-8') as f:
                t = f.read()
        else:
            logger.warn('  ! missing content file "%s"', self.src)
        return t


class Page(Content):
    data_dirname = 'pages'


class Post(Content):
    data_dirname = 'posts'
