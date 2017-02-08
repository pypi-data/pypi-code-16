# pylint: disable=W0622
"""cubicweb-seda application packaging information"""

from os import listdir as _listdir
from os.path import join, isdir
from glob import glob

modname = 'seda'
distname = 'cubicweb-seda'

numversion = (0, 6, 1)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
description = 'Data Exchange Standard for Archival'
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ = {
    'cubicweb': '>= 3.23', 'six': '>= 1.4.0',
    'cubicweb-eac': None,
    'cubicweb-skos': '>= 0.12.1',
    'cubicweb-compound': '>= 0.4',
    'cubicweb-relationwidget': '>= 0.4',
    'cubicweb-squareui': None,
    'pyxst': None,
    'rdflib': '>= 4.1',
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
            if fname[0] != '.' and not fname.endswith('.pyc') and
            not fname.endswith('~') and
            not isdir(join(dirpath, fname))]


data_files = [
    # common files
    [THIS_CUBE_DIR, [fname for fname in glob('*.py') if fname != 'setup.py']],
]
# check for possible extended cube layout
for dname in ('entities', 'views', 'sobjects', 'hooks', 'schema', 'data',
              'wdoc', 'i18n', 'migration', 'migration/data',
              'xsd'):
    if isdir(dname):
        data_files.append([join(THIS_CUBE_DIR, dname), listdir(dname)])
# Note: here, you'll need to add subdirectories if you want
# them to be included in the debian package
