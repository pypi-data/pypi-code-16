from setuptools import setup
from pypandoc import convert_file

long_description = convert_file('README.md', 'rst')

setup(
	name='hockeyapp-utils',
	description='Set of utility scripts for HockeyApp and CI integration',
	long_description=long_description,
	version='1.0.0',
	url='https://github.com/elevenetc/hockeyapp-utils',
	author='E. Levenetc',
	author_email='shumvlesu@gmail.com',
	license='MIT',
	classifiers=[
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 2.7'
	],
	packages=['hockeyapp-utils'],
	install_requires=[
		'requests',
	]
)