import sys
from distutils.core import setup, Extension

version = '0.0.3'

ext_kwds = dict(name = "pylgl",
                sources = [ "pylgl.c", "lglib.c", "lglopts.c", "lglbnr.c" ],
                define_macros = [ ('NLGLOG', True),
                                  ('NCHKSOL', True),
                                  ('NLGLDRUPLIG', True),
                                  ('NLGLYALSAT', True),
                                  ('NLGLFILES', True),
                                  ('NLGLDEMA', True) ])

if sys.platform != 'win32':
    ext_kwds['define_macros'].append(('PYLGL_VERSION', '"%s"' % version))

if '--inplace' in sys.argv:
    ext_kwds['define_macros'].append(('DONT_INCLUDE_LGL', True))
    ext_kwds['library_dirs'] = ['.']
    ext_kwds['libraries'] = ['pylgl']

setup(name = "pylgl",
      version = version,
      author = "Alexander Feldman",
      author_email = "alex@llama.gs",
      url = "https://github.com/abfeldman/pylgl",
      license = "MIT",
      classifiers = [ "Development Status :: 4 - Beta",
                      "Intended Audience :: Developers",
                      "Operating System :: OS Independent",
                      "Programming Language :: C",
                      "Programming Language :: Python :: 2",
                      "Programming Language :: Python :: 2.5",
                      "Programming Language :: Python :: 2.6",
                      "Programming Language :: Python :: 2.7",
                      "Programming Language :: Python :: 3",
                      "Programming Language :: Python :: 3.2",
                      "Programming Language :: Python :: 3.3",
                      "Topic :: Utilities" ],
      ext_modules = [ Extension(**ext_kwds) ],
      py_modules = [ 'test_pylgl' ],
      description = "bindings to lgl (a SAT solver)",
      long_description = open('README.rst').read())
