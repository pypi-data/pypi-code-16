from setuptools import setup

setup(name='smartstats',
      version='0.4a',
      description='Pretty Statistics',
      url='http://github.com/andrewbschneider/smartstats',
      author='Andrew Schneider',
      author_email='andrewbschneider@gmail.com',
      license='MIT',
      packages=['smartstats'],
      install_requires=['scipy','pandas','tableprint','statsmodels','numpy'],
      zip_safe=False)
