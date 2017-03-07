"""
XStatic resource package

See package 'XStatic' for documentation and basic tools.
"""

DISPLAY_NAME = 'Select2' # official name, upper/lowercase allowed, no spaces
PACKAGE_NAME = 'XStatic-%s' % DISPLAY_NAME # name used for PyPi

NAME = __name__.split('.')[-1] # package name (e.g. 'foo' or 'foo_bar')
                               # please use a all-lowercase valid python
                               # package name

VERSION = '4.0.3' # version of the packaged files, please use the upstream
                  # version number
BUILD = '1' # our package build number, so we can release new builds
            # with fixes for xstatic stuff.
PACKAGE_VERSION = VERSION + '.' + BUILD # version used for PyPi

DESCRIPTION = "%s %s (XStatic packaging standard)" % (DISPLAY_NAME, VERSION)

PLATFORMS = 'any'
CLASSIFIERS = []
KEYWORDS = '%s xstatic' % NAME

# XStatic-* package maintainer:
MAINTAINER = 'Benjamin Dauvergne'
MAINTAINER_EMAIL = 'bdauvergne@entrouvert.com'

# this refers to the project homepage of the stuff we packaged:
HOMEPAGE = 'http://select2.github.io/'

# this refers to all files:
LICENSE = '(same as %s)' % DISPLAY_NAME

from os.path import join, dirname
BASE_DIR = join(dirname(__file__), 'data')

LOCATIONS = {
    # CDN locations (if no public CDN exists, use an empty dict)
    # if value is a string, it is a base location, just append relative
    # path/filename. if value is a dict, do another lookup using the
    # relative path/filename you want.
    # your relative path/filenames should usually be without version
    # information, because either the base dir/url is exactly for this
    # version or the mapping will care for accessing this version.
    ('cloudflare', 'http'): {
        'select2.css': 'http://cdnjs.cloudflare.com/ajax/libs/select2/%s/css/select2.css' % VERSION,
        'select2.js': 'http://cdnjs.cloudflare.com/ajax/libs/select2/%s/js/select2.js' % VERSION,
        'select2.min.css': 'http://cdnjs.cloudflare.com/ajax/libs/select2/%s/css/select2.min.css' % VERSION,
        'select2.min.js': 'http://cdnjs.cloudflare.com/ajax/libs/select2/%s/js/select2.min.js' % VERSION,
    },
    ('cloudflare', 'https'): {
        'select2.css': 'https://cdnjs.cloudflare.com/ajax/libs/select2/%s/css/select2.css' % VERSION,
        'select2.js': 'https://cdnjs.cloudflare.com/ajax/libs/select2/%s/js/select2.js' % VERSION,
        'select2.min.css': 'https://cdnjs.cloudflare.com/ajax/libs/select2/%s/css/select2.min.css' % VERSION,
        'select2.min.js': 'https://cdnjs.cloudflare.com/ajax/libs/select2/%s/js/select2.min.js' % VERSION,
    },
}

