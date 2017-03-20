from __future__ import unicode_literals
from setuptools import setup
from codecs import open
from os import path

import simple_templates

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
try:
    import pypandoc
    long_description = pypandoc.convert(path.join(here, 'README.md'), 'rst')
except ImportError:
    long_description = open(path.join(here, 'README.md')).read()

setup(
    name='django-simple-templates',
    description='Easy, designer-friendly templates and A/B testing friendly tools for Django.',
    long_description=long_description,
    author='James Addison',
    author_email='addi00+github.com@gmail.com',
    packages=['simple_templates'],
    version=simple_templates.__version__,
    url='http://github.com/jaddison/django-simple-templates',
    keywords=['django', 'python', 'a/b testing', 'split testing', 'a/b', 'split'],
    license='BSD',
    classifiers=[
      'Development Status :: 5 - Production/Stable',
      'License :: OSI Approved :: BSD License',
      'Intended Audience :: Developers',
      'Environment :: Web Environment',
      'Programming Language :: Python',
      'Framework :: Django',
      'Topic :: Internet :: WWW/HTTP :: WSGI',
    ],
)