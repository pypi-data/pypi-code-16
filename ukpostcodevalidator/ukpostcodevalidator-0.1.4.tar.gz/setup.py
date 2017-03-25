from setuptools import setup

from ukpostcodevalidator import VERSION

setup(name='ukpostcodevalidator',
      version=VERSION,
      description='validates uk postal code',
      url='http://github.com/eddmash/ukpostcodevalidator',
      author='Eddilbert Macharia',
      author_email='edd.cowan@gmail.com',
      license='MIT',
      install_requires=['six'],
      packages=['ukpostcodevalidator'])
