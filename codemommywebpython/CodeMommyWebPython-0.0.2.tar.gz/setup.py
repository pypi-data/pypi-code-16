# from __future__ import with_statement
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
setup(name='CodeMommyWebPython',
      version='0.0.2',
      description='CodeMommy WebPython is a light, fast, free and open source Python MVC framework.',
      long_description='CodeMommy WebPython is a light, fast, free and open source Python MVC framework.',
      author='Candison',
      author_email='kandisheng@163.com',
      maintainer='Candison',
      maintainer_email='kandisheng@163.com',
      url='http://www.CodeMommy.com',
      packages=['CodeMommy', 'CodeMommy/core'],
      license='Apache 2.0',
      platforms=['Any'],
      install_requires=['jinja2>=2.9.5'],
      classifiers=[]
      )
