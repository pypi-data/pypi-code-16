from setuptools import setup, find_packages

package = 'iconvr'
version = '0.1.1'

setup(name=package,
      packages=find_packages(),
      version=version,
      author='zh5e',
      author_email='zhjie@live.com',
      description="文件转码工具",
      url='https://github.com/zh5e/iconvr',
      keywords=['iconv', 'gbk', 'encoding']
)
