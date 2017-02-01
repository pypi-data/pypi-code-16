from setuptools import setup

setup(
    name='DroneConnect',         # This is the name of your PyPI-package.
    version='0.1.3',                      # Update the version number for new releases
    scripts=['bin/droneconnect_client.py',],    # The name of your scipt, and also the command you'll be using for calling it
    url='https://github.com/cmagnuso/DroneConnect',
    author='Charlie Magnuson',
    author_email='magnuson.charlie@gmail.com',
    packages=['droneconnect',],
    license='LICENSE.txt',
    long_description=open('README.txt').read(),
)
