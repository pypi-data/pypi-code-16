from setuptools import setup
import os

package_requirements = os.path.join('cassandra_migrator.egg-info', 'requires.txt')
local_requirements = 'requirements.txt'

lines = []
if os.path.exists(package_requirements):
    with open(package_requirements, 'r') as f:
      lines = f.read().split('\n')
elif os.path.exists(local_requirements):
    with open(local_requirements, 'r') as f:
      lines = f.read().split('\n')

requirements = [package for package in lines if package and not package.startswith('#')]

setup(name='cassandra-migrator',
      version='0.1.4',
      description='cassanra migration tools',
      url='https://github.com/webscal3r/cassandra-migrator.git',
      author='Pitsanu Swangpheaw',
      author_email='pitsanu_s@hotmail.com',
      license='MIT',
      packages=['migrator'],
      zip_safe=False,
      install_requires=requirements,
      scripts=['scripts/cmig']
      )
