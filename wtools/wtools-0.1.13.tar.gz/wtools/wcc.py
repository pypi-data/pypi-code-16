#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com

import os
import sys
import platform
try:
	import ConfigParser as configparser
except:
	import configparser
import subprocess	

from waflib import Scripting, Errors, Logs, Utils, Context
from waflib.Build import BuildContext, CleanContext, InstallContext, UninstallContext
from waflib.Tools.compiler_c import c_compiler
from waflib.Tools.compiler_cxx import cxx_compiler


def options(opt):
	opt.add_option('--debug', dest='debug', default=False, action='store_true', help='debug build')	
	opt.add_option('--gcc', dest='gcc', default=False, action='store_true', help='use gcc compiler')	
	opt.add_option('--eroot', dest='eroot', default='', help='base path to external dependencies')
	opt.add_option('--sysroot', dest='sysroot', default='', help='cross-compile toolchain sysroot')
	opt.load('compiler_c')
	opt.load('compiler_cxx')


def configure(conf):
	conf.check_waf_version(mini='1.7.6', maxi='1.9.9')
	
	host = Utils.unversioned_sys_platform()
	if host not in c_compiler:
		host = 'default'
	if conf.options.gcc:
		c_compiler[host] = ['gcc']
		cxx_compiler[host] = ['g++']
	
	conf.load('compiler_c')
	conf.load('compiler_cxx')
	configure_gcc(conf)


def configure_gcc(conf):
	flags = ['-Wall', '-pthread']

	if conf.options.debug:
		flags.extend(['-g', '-ggdb'])
		defines = []
	else:
		flags.extend(['-O3'])
		defines = ['NDEBUG']

	if not '64' in conf.env.DEST_CPU:
		conf.env.LIBDIR = conf.env.LIBDIR.rstrip('64')

	for cc in ('CFLAGS', 'CXXFLAGS'):
		for flag in flags:
			conf.env.append_unique(cc, flag)
	for define in defines:
		conf.env.append_unique('DEFINES', define)

	conf.env.append_unique('INCLUDES', '%s/include' % conf.env.PREFIX)

	eroot = None
	if os.path.exists(conf.options.eroot):
		eroot = os.path.abspath(conf.options.eroot)
	else:
		eroot = os.getenv('EROOT')
	
	if eroot:
		path = os.path.abspath(eroot)
		conf.env.prepend_value('INCLUDES', "%s/include" % path)
		conf.env.prepend_value('LIBPATH', "%s/lib" % path)

	if os.path.exists(conf.options.sysroot):
		path = os.path.abspath(conf.options.eroot)
		conf.env.prepend_value('INCLUDES', "%s/include" % path)
		conf.env.prepend_value('LIBPATH', "%s/lib" % path)
		conf.env.prepend_value('LIBPATH', "%s/usr/lib" % path)


def post(bld):
	if '64' not in bld.env.DEST_CPU:
		return

	pre = bld.env.PREFIX
	lib = os.path.join(pre, 'lib')
	lib64  = os.path.join(pre, 'lib64')
	cwd = os.getcwd()
	
	try:
		os.chdir(pre)
		if not os.path.exists(lib) and os.path.exists(lib64):
			os.symlink("lib64", "lib")
		elif os.path.exists(lib) and not os.path.exists(lib64):
			os.symlink("lib", "lib64")
	finally:
		os.chdir(cwd)


