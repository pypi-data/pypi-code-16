import sys
sys.dont_write_bytecode = True
from os.path import join, dirname
from distutils.core import setup


def read(fname):
    return open(join(dirname(__file__), fname)).read()

setup(name='pylumberjack',
      version='0.0.1',
      description='Python Logging for Humans',
      author='Santosh Venkatraman',
      url='https://github.com/thesantosh/lumberjack',
      author_email='santosh.venk@gmail.com',
      packages=['lumberjack'],
      long_description=read('README.rst'),
      license="MIT",
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
      ],
)
