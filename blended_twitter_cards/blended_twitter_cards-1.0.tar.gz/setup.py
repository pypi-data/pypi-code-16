from setuptools import setup

setup(name='blended_twitter_cards',
      version='1.0',
      description='Easy Twitter cards plugin for Blended',
      url='http://jmroper.com/blended/',
      author='John Roper',
      author_email='johnroper100@gmail.com',
      license='GPL3.0',
      packages=['twitter_cards'],
      install_requires=[
          'blended',
      ],
      zip_safe=False)
