""" A wechat ui project
See:
https://github.com/littlecodersh/itchatui
"""

from setuptools import setup, find_packages
from codecs import open
from os import path
import itchatui

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='itchatui',

    version=itchatui.__version__,

    description='A wechat ui based on qt',
    long_description=long_description,

    url='https://github.com/littlecodersh/itchatui',

    author='LittleCoder',
    author_email='i7meavnktqegm1b@qq.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],

    keywords='wechat itchatui qt weixin ui',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(),

    install_requires=[],

    # List additional groups of dependencies here
    extras_require={},
)
