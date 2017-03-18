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

	cc = conf.env.CC[0]
	if cc.endswith('-gcc'):
		s = conf.find_program(cc, mandatory=True)
		conf.env.append_unique('PATH', os.path.dirname(s[0]))
	
	conf.env.PREFIX = str(conf.env.PREFIX).replace('\\', '/')
	conf.env.append_unique('INCLUDES', '%s/include' % conf.env.PREFIX)
	configure_gcc(conf)


def gcc_incdirs(conf):
	if not sys.platform.startswith("linux"):
		return []

	if conf.env.DEST_CPU != platform.processor():
		return []
		
	cmd="%s -print-prog-name=cc1" % conf.env.CC[0]	
	res = subprocess.check_output(cmd.split())
	
	cmd="echo | %s -v" % (res.split()[0])
	res = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
	
	return [l.strip() for l in res.splitlines() if l.startswith(" /")]
	

def gcc_libpaths(conf):
	if not sys.platform.startswith("linux"):
		return []
		
	cmd=os.path.basename(conf.env.CC[0])
	mingw = cmd.endswith('-mingw32-gcc')
	
	if cmd.endswith("-gcc"):
		cmd="%s-ld" % cmd.rstrip("-gcc")
	else:
		cmd="ld"
	cmd+=" --verbose | grep SEARCH_DIR"
	
	ld = subprocess.check_output(cmd, shell=True).split()
	ld = [l.strip('SEARCH_DIR("').strip('");') for l in ld]
	
	cmd="%s --print-search-dirs" % conf.env.CC[0]	
	sd = subprocess.check_output(cmd.split()).split()[-1]
	
	libpaths = [conf.env.LIBDIR]
	for s in set(sd.split(":") + ld):
		s = s.lstrip("=")
		if os.path.exists(s):
			s = os.path.realpath(s)
			libpaths.append(s)
			if mingw:
				libpaths.append(s.replace('/lib', '/bin'))

	if conf.env.DEST_CPU == platform.processor() and conf.env.DEST_OS == "linux":
		if os.path.exists("/etc/ld.so.conf.d"):
			for root, dirs, files in os.walk("/etc/ld.so.conf.d"):
				for f in files:
					paths = subprocess.check_output(["cat", os.path.join(root, f)])
					for p in paths.split('\n'):
						if not p.startswith('#') and len(p) and os.path.exists(p):
							libpaths.append(p)

	libpaths = list(set(libpaths))
							
	if conf.env.DEST_CPU != platform.processor():
		for s in ('/lib', '/usr/lib', '/usr/local/lib'):
			if s in libpaths:
				libpaths.remove(s)
	
		conf.env.LIBPATH = []
	
	return libpaths


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

	for include in gcc_incdirs(conf):
		conf.env.prepend_value('INCLUDES', include)

	for libpath in gcc_libpaths(conf):
		conf.env.prepend_value('LIBPATH', libpath)
		
	if os.path.exists('gccdump.s'):
		os.remove('gccdump.s')

