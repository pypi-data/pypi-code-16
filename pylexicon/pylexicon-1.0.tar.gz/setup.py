from setuptools import setup

setup(name='pylexicon',
      version='1.0',
      description='A python module to get meanings, synonyms and antonyms',
      url='http://github.com/LordFlashmeow/pylexicon',
      author='LordFlashmeow',
      author_email='dash098@gmail.com',
      license='MIT',
      packages=['pylexicon'],
      install_requires=[
          'requests',
          'BeautifulSoup4'
      ])
