from setuptools import setup

setup(name='blended_import_bootstrap',
      version='1.0',
      description='Easy import Bootstrap for Blended',
      url='http://jmroper.com/blended/',
      author='John Roper',
      author_email='johnroper100@gmail.com',
      license='GPL3.0',
      packages=['import_bootstrap'],
      install_requires=[
          'blended',
      ],
      zip_safe=False)
