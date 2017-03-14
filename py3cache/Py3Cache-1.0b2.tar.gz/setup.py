# -*- coding: utf-8 -*-
from distutils.core import setup
import io
import re
import os


DOC = '''TODO'''


def read(*names, **kwargs):
    return io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ).read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(name='Py3Cache',
      version=find_version('py3cache/__init__.py'),
      description=u'该项目是 J2Cache 的 Python 语言移植版本。',
      long_description=DOC,
      author='oschina',
      author_email='liudong@oschina.cn',
      url='http://git.oschina.net/ld/Py3Cache',
      license='Apache',
      install_requires=[
        'redis'
      ],
      classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities'
      ],
      keywords='Py3Cache, J2Cache',
      zip_safe=False,
      packages=['py3cache'],
      package_data={'': ['config.ini']},
      include_package_data=True,
)
