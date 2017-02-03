from setuptools import setup

setup(name='autocharles',
      version='1.8',
      description='Script for automating the parsing of Charles XML sessions',
      url='http://github.com/mdiblasio/autocharles',
      author='Michael DiBlasio',
      author_email='mdiblasio@google.com',
      license='',
      scripts=['bin/autocharles'],
      packages=['autocharles'],
      zip_safe=False)
