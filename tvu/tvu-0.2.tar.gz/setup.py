# -*- coding: utf-8 -*-
import sys
try:
    from setuptools import setup
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup


__version__ = '0.2'


tests_require = ['nose == 1.3.7']
install_require = []
if sys.version_info < (3, 4):
    install_require.append('enum34 == 1.1.6')

short_descr = \
    'Library for typechecking/validation/unification of function arguments.'
download_url = 'http://github.com/Paczesiowa/tvu/tarball/v' + __version__

setup(name='tvu',
      version=__version__,
      packages=['tvu'],
      description=short_descr,
      long_description=open('README.md', 'r').read(),
      author=u'Bartek Ćwikłowski',
      author_email='paczesiowa@gmail.com',
      url='https://github.com/Paczesiowa/tvu',
      download_url=download_url,
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: Public Domain',
                   'Operating System :: POSIX',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.6'],
      license='UNLICENSE/Public Domain',
      keywords=['typecheck', 'decorator'],
      zip_safe=True,
      install_requires=install_require,
      test_suite='nose.collector',
      tests_require=tests_require)
