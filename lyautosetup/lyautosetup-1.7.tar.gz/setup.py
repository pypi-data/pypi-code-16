# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from autosetup.app import __author__, __version__, __doc__

setup(name='lyautosetup',
      version=__version__,
      author=__author__,
      author_email='1313475@qq.com',
      license="http://www.apache.org/licenses/LICENSE-2.0",
      description=__doc__,
      packages=find_packages(),
      include_package_data=True,  # 启用清单文件MANIFEST.in
      exclude_package_data={'': ['.gitignore']},
      zip_safe=False,
      install_requires=['jinja2>=2.9', 'pyyaml'],
      entry_points='''
        [console_scripts]
        autosetup=autosetup.app:main
    ''')
