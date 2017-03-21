# -*- coding: utf-8 -*-

import os
import logging

from collections import OrderedDict
from string import Template


logger = logging.getLogger('wt.base')


class ObjectDict(dict):

    def __getattr__(self, name, default=None):
        return self.env_value(self.get(name, default))

    def __setattr__(self, name, value):
        self[name] = value

    def env_value(self, v):
        if isinstance(v, str):
            return Template(v).safe_substitute(**os.environ)
        return v

    def path(self, path, dflt=None):
        parts = path.split('.')
        src = self
        for idx, p in enumerate(parts[:-1]):
            src = src.get(p)
            if src is None:
                break
            if not isinstance(src, dict):
                msg = ('Expecting %s instance to have value for "%s"'
                       ' but "%s" found at "%s" instead of nested dict'
                       % (type(self).__name__,
                          path,
                          str(src),
                          '.'.join(parts[:idx + 1])))
                raise ValueError(msg)
        v = src and src.get(parts[-1], dflt)
        if isinstance(v, dict):
            v = ObjectDict(v)
        return self.env_value(dflt if v is None else v)


class OrderedObjectDict(OrderedDict, ObjectDict):
    pass


class Config(ObjectDict):
    pass


class Content(ObjectDict):
    content_dirname = 'content'
    data_dirname = None

    @classmethod
    def from_dict(cls, workdir, data):
        p = cls(data)
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
