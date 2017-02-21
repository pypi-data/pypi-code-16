# coding=utf-8

import codecs
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def read(filename):
    """
    :param filename: 需要读入的文件路径（相对当前目录）
    :return: 读入的文件内容
    """
    with codecs.open(os.path.join(os.path.dirname(__file__), filename)) as fileobject:
        return fileobject.read()


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}

NAME = 'base_bridge'

PACKAGE = "base_bridge"

PACKAGES = get_packages(NAME)

PACKAGE_DATA = get_package_data(NAME)

DESCRIPTION = "A base bridge between django framework and our private application."

LONG_DESCRIPTION = read('README.md')

KEYWORDS = "django base bridge model field db"

AUTHOR = __import__(PACKAGE).__author__

AUTHOR_EMAIL = "fjliufeng@163.com"

URL = "https://github.com/evilloop/django-base-bridge"

VERSION = __import__(PACKAGE).__version__

LICENSE = "GNU General Public License v2 (GPLv2)"

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Environment :: Web Environment',
        'Topic :: Internet :: WWW/HTTP',
    ],
    keywords=KEYWORDS,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    packages=PACKAGES,
    include_package_data=True,
    zip_safe=True,
)
