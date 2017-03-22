# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- YAML based data loader
# :Created:   mer 10 feb 2010 14:35:05 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: Copyright (C) 2010-2016 Lele Gaifax
#

from os.path import join, normpath

import yaml


def resolve_class_name(classname):
    """Import a particular Python class given its full dotted name.

    :param classname: full dotted name of the class,
                      such as "package.module.ClassName"
    :rtype: the Python class
    """

    modulename, _, classname = classname.rpartition('.')
    module = __import__(modulename, fromlist=[classname])
    return getattr(module, classname)


class File(yaml.YAMLObject):
    """Facility to read the content of an external file.

    The value of field may be loaded from an external file, given its pathname which is
    interpreted as relative to the position of the YAML file currently loading::

        - entity: cpi.models.Document
          key: filename
          data:
            - filename: image.gif
              content: !File {path: ../image.gif}
    """

    yaml_tag = '!File'

    basedir = None

    def __init__(self, path):
        self.path = path

    def read(self):
        # PyYAML does not execute the __init__ method
        try:
            path = self.path
        except AttributeError:
            raise RuntimeError('The !File object requires a "path" argument')
        fullpath = normpath(join(self.basedir, path))
        return open(fullpath, 'rb').read()


class SQL(yaml.YAMLObject):
    """Raw SQL statement."""

    yaml_tag = '!SQL'

    def __init__(self, query, params=None):
        self.query = query
        self.params = params

    def fetch(self, session):
        # PyYAML does not execute the __init__ method
        try:
            query = self.query
        except AttributeError:
            raise RuntimeError('The !SQL object requires a "query" argument')
        try:
            params = self.params
        except AttributeError:
            params = None
        return session.scalar(query, params)
