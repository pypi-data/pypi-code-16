from setuptools import setup

setup(name='blended_google_analytics',
      version='1.0',
      description='Easy google analytics plugin for Blended',
      url='http://jmroper.com/blended/',
      author='John Roper',
      author_email='johnroper100@gmail.com',
      license='GPL3.0',
      packages=['blended_google_analytics'],
      install_requires=[
          'blended',
      ],
      zip_safe=False)
