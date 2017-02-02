#
#To upload the latest version, change "version=0.X.X+1" and type:
#    python setup.py sdist upload
#
#
#

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='pds_cdf',
      version='0.1.2',
      description='A python CDF reader',
      url='http://github.com/MAVENSDC/PDScdf',
      author='MAVEN SDC',
      author_email='mavensdc@lasp.colorado.edu',
      license='MIT',
      keywords='tplot maven lasp idl',
      packages=['pds_cdf'],
      install_requires=['numpy'],
      include_package_data=True,
      zip_safe=False)