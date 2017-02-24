from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    readme = f.read()

setup(
    name="haruzira_sdk",
    version="2.1.0",
    packages=['haruzirasdk',],
    description='This package is a SDK for tcp communication with Haruzira(Windows UWP APP).',
    long_description=readme,
    url='http://haruzirasdke.wpblog.jp/',
    author='Symmetry Soft',
    author_email='git@symmetry-soft.com',
    license='MIT',
    keywords='network tcp tts sdk development',
    install_requires=[
        'numpy', 'pycrypto'
    ],
    extras_require={
        # Python 3.4 未満にはenumが標準ライブラリにない
        #':python_version<"3.4"': [
        #    'enum34',
        #],
        #':python_version in "3.2,3.3"': [
        #    'enum34',
        #],
    },
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Topic :: Communications',
        'Topic :: Multimedia',
        'Topic :: Text Processing',
        'License :: OSI Approved :: MIT License',
        #'Programming Language :: Python :: 2',
        #'Programming Language :: Python :: 2.7',
        #'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)

