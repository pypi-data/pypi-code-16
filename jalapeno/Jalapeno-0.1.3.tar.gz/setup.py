#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from setuptools import setup
import platform

GUI_Frame='cefpython3'
if platform.system() == 'Darwin':
	GUI_Frame='PyQt5'

setup(
	name='Jalapeno',
	version='0.1.3',
	author='Chenghao Qian',
	author_email='qch.jacob.jm@gmail.com',
	include_package_data=True,
	packages=['Jalapeno',
				'Jalapeno.lib',
				'Jalapeno.utils',
				'Jalapeno.views',
				'Jalapeno.GUI'
				],
	scripts=['Jaloc','Jalo','JaloLite'],
	url='https://github.com/ChenghaoQ/Jalapeno',
	license='LGPL',
	description='Static Site Generator based on Flask',
	keywords= ['Flask','Blog','site Generator','static site'],
	install_requires=['Markdown >= 2.6.6',
						'Flask >= 0.10.1',
						'Pygments >= 2.1.3 ',
						'MarkupSafe >= 0.23',
						'Flask-FlatPages >= 0.6',
						'Frozen-Flask >= 0.12',
						GUI_Frame ]
)