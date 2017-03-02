"""
:Authors: cykooz
:Date: 14.03.2016
"""
import logging
import os
import stat

import sys

from zc.buildout import UserError
from zc.buildout.easy_install import script_header, _safe_arg
from zc.recipe.egg.egg import Eggs


WRAPPER_TEMPLATE = script_header + '''
import sys
sys.path[0:0] = [
    %(syspath)s,
]
%(environ)s
%(initialization)s
from %(module)s import %(func)s as get_app
application = get_app()
'''


class Recipe(object):
    """Buildout recipe: cykooz.recipe.wsgi:default"""

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.script_name = options.get('script-name', self.name)
        self.target = options.get('target', '')
        self.app_fabric = options.get('app_fabric', '')

    def install(self):
        egg = Eggs(self.buildout, self.options['recipe'], self.options)
        requirements, ws = egg.working_set()
        path = [pkg.location for pkg in ws]
        extra_paths = self.options.get('extra-paths', '')
        extra_paths = extra_paths.split()
        path.extend(extra_paths)
        environ = self.options.get('environ', '')
        initialization = self.options.get('initialization', '')
        if environ:
            environ = ["os.environ['%s'] = '%s'" % tuple(s.strip() for s in i.split('=', 1))
                       for i in environ.splitlines() if '=' in i]
            environ.insert(0, 'import os')
            environ = '\n'.join(environ)

        if ':' not in self.app_fabric:
            logging.getLogger(self.name).error(
                'Cannot parse the app_fabric %s.', self.app_fabric)
            raise UserError('Invalid app fabric')

        module, func = self.app_fabric.split(':', 1)
        python = _safe_arg(sys.executable)
        output = WRAPPER_TEMPLATE % dict(
            python=python,
            environ=environ,
            initialization=initialization,
            syspath=',\n    '.join(repr(p) for p in path),
            module=module,
            func=func,
        )
        if not self.target:
            location = self.buildout['buildout']['bin-directory']
            self.target = os.path.join(location, self.script_name)

        f = open(self.target, 'wt')
        try:
            f.write(output)
        finally:
            f.close()

        exec_mask = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        os.chmod(self.target, os.stat(self.target).st_mode | exec_mask)

        self.options.created(self.target)
        return self.options.created()

    def update(self):
        self.install()
