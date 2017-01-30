import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.RST')).read()
CHANGES = open(os.path.join(here, 'CHANGES.RST')).read()

requires = [
    'kajiki',
    'sqlalchemy',
    'formencode',
    'pyramid',
    'decorator',
    'transaction',
    'zope.sqlalchemy'
    ]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest',  # includes virtualenv
    'pytest-cov',
    ]

setup(name='PyWebTools',
      version='1.1.3',
      description='A collection of helpers for use with Pyramid, Kajiki, Formencode, and SQLAlchemy',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
                   'Development Status :: 4 - Beta',
                   'Programming Language :: Python :: 3',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
                   'Operating System :: OS Independent'
        ],
      author='Mark Hall',
      author_email='Mark.Hall@work.room3b.eu',
      url='http://bitbucket.org/mhall/pywebtools/overview',
      keywords='web pyramid kajiki formencode SQLAlchemy',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      install_requires = requires,
      extras_require={
          'testing': tests_require,
      },
      entry_points="""
      [pytest11]
      pywebtools_testing = pywebtools.testing
      """
      )
