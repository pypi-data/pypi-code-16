#!/usr/bin/env python
# -*- coding: utf-8 -*-

## 
from distutils.core import setup 

setup(
	name='colinops',
	author='Colin',
	author_email='colin50631@gmail.com',
	version='1.0.3',
	package_dir={'':'src'},
	packages=['colinops','colinops.devops','colinops.opsmonitor'],
	#py_modules=['colinops._opslogs','colinops._opsdate'],
	url='https://github.com/opscolin/devops.git',
	license='MIT',
	description='colinops package',
	long_description='customize common api for devops by python',
	platforms='Linux,unix',
	keywords='devops, opsdate, opslogs',
	classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
)
