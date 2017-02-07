import os, sys, subprocess
from setuptools import setup
from setuptools.command.install import install
class CustomInstall(install):
	def run(self):
		install.run(self)
		print "here is custom command"
		subprocess.call(['setupAuto.sh'])

setup (name='piforge',
	version='1.1.2',
	description='iforge for rPi server component',
	url='',
	author='Trevor Shaw',
	author_email='shawt@genlrn.com',
	license='MIT',
	scripts=['bin/piforge','piforge/setupAuto.sh'],
	packages=['piforge'],
	install_requires=[
		'web.py',
	],
	zip_safe=False,
	cmdclass={'install': CustomInstall})
		
