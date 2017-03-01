from setuptools import setup, find_packages

package = 'iconvr'
version = '0.1.4'

setup(name=package,
      packages=find_packages(),
      version=version,
      author='zh5e',
      author_email='zhjie@live.com',
      description="文件编码转换工具",
      url='https://github.com/zh5e/iconvr',
      keywords=['iconv', 'gbk', 'encoding']
)
