#encoding:utf-8
#从python发布工具导入setup函数
from distutils.core import setup

setup(
	name		= 'recursive_print_list',
	version 	= '1.0.2',
#将模块的元数据与setup函数的参数关联
	py_modules	= ['recursive_print_list'],
	author		=  'stephanie',
	author_email	=  '13663788159@163.com',
#	url		= 'http://',
	description 	= 'A simple recursiving print list item fun',

	)
