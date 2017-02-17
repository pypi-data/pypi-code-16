from setuptools import setup

def readme():
	with open('README.rst') as f:
		return f.read()


setup(
	name='pythonPlayGround',
	version='0.2',
	description='play ground for python',
	#long_description='local test package',
	long_description=readme(),
	classifiers=[
		'Development Status :: 3 - Alpha',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 2.7',
		'Topic :: Text Processing :: Linguistic'
	],
	keywords='test internal',
	url='http://rkalva89828.kau.roche.com/daij12/pythonPlayGround',
	author='Jian Dai',
	author_email='daij12@gene.com',
	license='MIT',
	packages=['pythonPlayGround'],
	install_requires=[
		'pandas',
		'JayDeBeApi',
		'JPype1'
	],
	dependency_links=[], #Packages Not On PyPI
	include_package_data=True,
	zip_safe=False)



