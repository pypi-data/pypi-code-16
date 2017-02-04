#!/usr/bin/env python

long_desc = """\
An alternative to the standard python traceback module which allows
you to show a traceback in a customized way.

It is also possible to monkey_patch the standard python traceback module.
"""
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def main():
    setup(name='traceb',
          version='0.1.1',
          description='traceback with verbose and compact options',
          long_description=long_desc,
          author='Tiago Coutinho',
          author_email='coutinhotiago@gmail.com',
          url='http://github.com/tiagocoutinho/traceb',
          py_modules=['traceb'],
          license='MIT',
          platforms='any',
          classifiers=['Development Status :: 4 - Beta',
                       'Intended Audience :: Developers',
                       'License :: OSI Approved :: MIT License',
                       'Programming Language :: Python :: 2.6',
                       'Programming Language :: Python :: 2.7',
                       'Programming Language :: Python :: 3',
                       'Programming Language :: Python :: 3.2',
                       'Programming Language :: Python :: 3.3',
                       'Programming Language :: Python :: 3.4',
                       'Programming Language :: Python :: 3.5',],)

if __name__ == '__main__':
    main()
