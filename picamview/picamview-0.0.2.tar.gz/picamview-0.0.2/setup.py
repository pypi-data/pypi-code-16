from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_desc = f.read()

setup(
	name='picamview',
	version='0.0.2',
	description='Camera Viewer for the Raspberry Pi',
	long_description=long_desc,
	url='https://github.com/stelzch/picamview',
	author='Christoph Stelz',
	author_email='mail@ch-st.de',
	license='MIT',
	classifiers=[
	        'Development Status :: 3 - Alpha',
	        'Environment :: X11 Applications',
	        'Intended Audience :: Education',
	        'License :: OSI Approved :: MIT License',
	        'Natural Language :: English',
	        'Operating System :: POSIX :: Linux',
	        'Programming Language :: Python :: 3 :: Only',
	        'Topic :: Multimedia :: Video :: Capture',
	        'Topic :: Multimedia :: Video :: Conversion'
	],
	keywords='camera raspberry capture viewer',
	packages=[],
	entry_points={
		'console_scripts':[
			'PiCamView=picamview:run',
		],
	},
)
