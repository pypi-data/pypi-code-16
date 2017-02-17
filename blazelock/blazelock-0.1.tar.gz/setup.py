from blazelock import __version__
from distutils.core import setup
# from setuptools import setup

VERSION = '0.1'

setup(
      name='blazelock',
      version=__version__,
      description='Distributed Reader-Writer Lock using Redis',
      author='Kunal Lillaney',
      author_email='lillaney@jhu.edu',
      url='https://github.io/kunallillaney/blazelock',
      license='Apache2.0',
      packages=[
        'blazelock'
      ],
      # setup_requires=[
      # ],
      install_requires=[
        'redis>=2.10.5',
        'hiredis>=0.2.0'
      ]
)
