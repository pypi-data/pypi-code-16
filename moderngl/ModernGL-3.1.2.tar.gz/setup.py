from setuptools import setup, Extension
import os, platform

target = platform.system().lower()

if target == 'linux':
	from distutils import sysconfig
	sysconfig._config_vars['OPT'] = sysconfig.get_config_vars()['OPT'].replace('-Wstrict-prototypes', '')

libraries = {
	'windows': ['gdi32', 'opengl32', 'user32'],
	'linux': ['GL', 'dl', 'X11'],
}

extra_args = {
	'windows': [],
	'linux': ['-std=c++11'],
}

# Some notes during the install on Ubuntu:
# apt-get install libgl1-mesa-dev libx11-dev

def sources():
	for path, folders, files in os.walk('src'):
		for f in files:
			if f.endswith('.cpp'):
				yield os.path.join(path, f)

ModernGL = Extension(
	name = 'ModernGL.ModernGL',
	include_dirs = ['src'],
	# define_macros = [('MGL_VERBOSE', '1')],
	libraries = libraries[target],
	extra_compile_args = extra_args[target],
	sources = list(sources()),
)

setup(
	name = 'ModernGL',
	version = '3.1.2',
	packages = ['ModernGL'],
	ext_modules = [ModernGL],
)
