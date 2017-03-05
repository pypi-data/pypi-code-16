from setuptools import setup

setup(name='smartstats',
      version='0.02',
      description='Pretty Statistics',
      url='http://github.com/andrewbschneider/smartstats',
      author='Andrew Schneider',
      author_email='andrewbschneider@gmail.com',
      license='MIT',
      packages=['smartstats'],
      install_requires=['scipy','pandas','tableprint','statsmodels'],
      zip_safe=False)
