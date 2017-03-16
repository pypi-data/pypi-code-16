from distutils.core import setup, Extension

mmh3module = Extension('mmh3', sources=['mmh3module.cpp', 'murmur_hash_3.cpp'])

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: Public Domain',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'Topic :: Utilities'
]

setup(
    name='splitmmh3',
    version='0.1',
    description=('An adaption of a public domain library'
                 'with python2.7 support'),
    license='Public Domain',
    author='V G, Split Software',
    author_email='veegee@veegee.org, www.split.io',
    url='http://packages.python.org/splitmmh3',
    ext_modules=[mmh3module],
    keywords=['hash', 'MurmurHash'],
    long_description=open('README.rst').read(),
    classifiers=classifiers
)
