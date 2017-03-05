"""Installs QuickWeb using distutils

Run:
    python setup.py install

to install this package.
"""

from setuptools import setup

name = "QuickWeb"
version = "0.4.0"

desc = "Rapid Development Python Web Framework"
long_desc = "QuickWeb is a rapid web development python framework"


classifiers = '''
Development Status :: 1 - Planning
Intended Audience :: Developers
License :: Freely Distributable
License :: OSI Approved :: BSD License
Operating System :: OS Independent
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3.3
Programming Language :: Python :: 3.5
Topic :: Internet :: WWW/HTTP :: WSGI
Topic :: Internet :: WWW/HTTP :: WSGI :: Application
Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware
Topic :: Internet :: WWW/HTTP :: WSGI :: Server
'''

requirements = '''
CherryPy
Dominate
Mako
docopt>=0.6.2
Requests
'''

setup(
    name=name,
    version=version,
    description=desc,
    long_description=long_desc,
    author='MyWayOS Team',
    author_email='team@mywayos.org',
    classifiers=[x for x in classifiers.splitlines() if x],
    install_requires=[x for x in requirements.splitlines() if x],
    url='http://quickweb.mywayos.org/',
    packages=[
        "quickweb",
        "quickweb/wsgi",
    ],
    data_files=[('share/quickweb',  ['requirements.txt', 'application.py'])],
    package_data={'quickweb/wsgi': ['*.txt']},
    include_package_data=True,
    scripts=["scripts/quickweb"]
)
