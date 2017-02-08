# pylint: disable=W0622
"""cubicweb-agape2 application packaging information"""

from os import listdir as _listdir
from os.path import join, isdir
from glob import glob


modname = 'sherpa'
distname = 'cubicweb-sherpa'

numversion = (0, 1, 1)
version = '.'.join(str(num) for num in numversion)

license = 'GPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
description = 'SEDA v2 profile generator'
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ = {
    'cubicweb': '>= 3.24.0', 'six': '>= 1.4.0',
    'cubicweb-seda': None,
    'cubicweb-registration': None,
    'cubicweb-rememberme': None,
    'jinja2': None,
}

__recommends__ = {}

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
]

THIS_CUBE_DIR = join('share', 'cubicweb', 'cubes', modname)


def listdir(dirpath):
    return [join(dirpath, fname) for fname in _listdir(dirpath)
            if fname[0] != '.' and not fname.endswith('.pyc')
            and not fname.endswith('~')
            and not isdir(join(dirpath, fname))]


data_files = [
    # common files
    [THIS_CUBE_DIR, [fname for fname in glob('*.py') if fname != 'setup.py']],
]
# check for possible extended cube layout
for dname in ('entities', 'views', 'sobjects', 'hooks', 'schema', 'data',
              'wdoc', 'i18n', 'migration', 'views/templates'):
    if isdir(dname):
        data_files.append([join(THIS_CUBE_DIR, dname), listdir(dname)])
# Note: here, you'll need to add subdirectories if you want
# them to be included in the debian package
