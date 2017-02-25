try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

package = 'iconvr'
version = '0.1'

setup(name=package,
      version=version,
      author='zh5e',
      author_email='zhjie@live.com',
      description="文件转码工具",
      url='https://github.com/zh5e/iconvr')
