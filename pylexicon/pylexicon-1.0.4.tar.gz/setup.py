from setuptools import setup

setup(name='pylexicon',
      version='1.0.4',
      description='A python module to get meanings, synonyms and antonyms of words',
      url='http://github.com/LordFlashmeow/pylexicon',
      author='LordFlashmeow',
      author_email='dash098@gmail.com',
      license='MIT',
      packages=['pylexicon'],
      install_requires=[
          'requests',
          'BeautifulSoup4'
      ],
      keywords='dictionary lexicon define meaning synonym antonym',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers'
      ]

      )
