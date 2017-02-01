from setuptools import setup

setup(
    name='DroneConnect',         # This is the name of your PyPI-package.
    version='0.1.4',                      # Update the version number for new releases
    scripts=['bin/droneconnect_client.py', 'bin/droneconnect_pb2.py',],    
    url='https://github.com/cmagnuso/DroneConnect',
    author='Charlie Magnuson',
    author_email='magnuson.charlie@gmail.com',
    packages=['droneconnect',],
    license='LICENSE.txt',
    long_description=open('README.txt').read(),
)
