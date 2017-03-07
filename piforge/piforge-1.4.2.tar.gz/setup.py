import os, sys, subprocess
from setuptools import setup
from setuptools.command.install import install
class CustomInstall(install):
	def run(self):
		install.run(self)
		print "here is custom command"
		subprocess.call(['setupAuto.sh'])

setup (name='piforge',
    #you must also change the global ver variable in __main__.py
	version='1.4.2',
	description='iforge for rPi server component',
	url='https://github.com/shawt/piforge',
	author='Trevor Shaw',
	author_email='shawt@genlrn.com',
	license='MIT',
	scripts=['piforge/setupAuto.sh'],
	entry_points={
          'console_scripts': [
              'piforge = piforge.__main__:main'
          ]
      },
	packages=['piforge'],
	install_requires=[
		'web.py',
		'RPi.GPIO',
		'picamera',
		'adafruit-pca9685',
		'adafruit-ads1x15',
		
	],
	zip_safe=False,
	cmdclass={'install': CustomInstall})
		
