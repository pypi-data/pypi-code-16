"""
Hans Roh 2015 -- http://osp.skitai.com
License: BSD
"""
import re
import sys
import os
import shutil, glob
from distutils.core import setup
from setuptools.command.easy_install import easy_install

class easy_install_default(easy_install):
	def __init__(self):
		from distutils.dist import Distribution		
		self.distribution = Distribution()
		self.initialize_options()

e = easy_install_default()
try: e.finalize_options()
except: pass
python_package_dir = e.install_dir

def mkdir (tdir, mod = -1):
	while tdir:
		if tdir [-1] in ("\\/"):
			tdir = tdir [:-1]
		else:
			break	

	if os.path.isdir (tdir): return	
	chain = [tdir]	
	while 1:
		tdir, last = os.path.split (tdir)		
		if not last: 
			break
		if tdir:
			chain.insert (0, tdir)
	
	for dir in chain [1:]:
		try: 
			os.mkdir (dir)
			if os.name == "posix" and mod != -1:
				os.chmod (dir, mod)				
		except OSError as why:
			if why.errno in (17, 183): continue
			else: raise
				
if sys.argv[-1] == 'publish':
	if os.name == "nt":
		os.system('python setup.py sdist upload') # bdist_wininst --target-version=2.7
	else:		
		os.system('python setup.py sdist upload')
	sys.exit()

classifiers = [
  'License :: OSI Approved :: BSD License',
  'Development Status :: 4 - Beta',
  'Topic :: Internet :: WWW/HTTP',
	'Topic :: Internet :: WWW/HTTP :: HTTP Servers',				
	'Environment :: Console',
	'Environment :: No Input/Output (Daemon)',
	'Topic :: Software Development :: Libraries :: Python Modules',
	'Intended Audience :: Developers',
	'Intended Audience :: Science/Research',
	'Programming Language :: Python',
	'Programming Language :: Python :: 2.7',
	'Programming Language :: Python :: 3'
]


packages = ['skitaid']
package_dir = {'skitaid': 'skitaid'}

skitaid_files = [
	"bin/*.py",
	"etc/init/skitaid.conf",
	"etc/init.d/skitaid", 
	"etc/skitaid/skitaid.conf",
	"etc/skitaid/servers-available/README.txt", 
	"etc/skitaid/servers-enabled-posix/example.conf",
	"etc/skitaid/servers-enabled-nt/example.conf",
	"etc/skitaid/certifications/*.*",
	"wsgi/example/*.py",
	"wsgi/example/static/*.*",	
	"wsgi/example/resources/*.*",	
	"wsgi/example/templates/*.*",
	"wsgi/example/apppackages/*.*",
]

package_data = {
	"skitaid": skitaid_files
}

examples = [ 
	os.path.join ("skitaid/wsgi/example", each) for each in (
		"app.py", "gateway.py", "grpc_route_guide.py", "proxy.py", "reverse_proxy.py", "rpc2.py", 
		"tls12.py", "websocket.py", "websocket-flask.py", "auth.py", "app_single_thread.py"
	)
]

templates = [ 
	os.path.join ("skitaid/wsgi/example/templates", each) for each in (
		"index.html", "documentation.html", "documentation2.html", "websocket.html", "websocket-flask.html"
	)
]

apppackages = [ 
	os.path.join ("skitaid/wsgi/example/apppackages", each) for each in (
		"__init__.py", "route_guide_pb2.py"
	)
]

							
if os.name == "nt":
	if not os.path.isfile ("c:\\skitaid\\etc\\skitaid.conf"):
		mkdir ("c:\\skitaid\\etc\\servers-enabled")	
		shutil.copyfile ("skitaid/etc/skitaid/skitaid.conf", "c:\\skitaid\\etc\\skitaid.conf")
		shutil.copyfile ("skitaid/etc/skitaid/servers-enabled-nt/example.conf", "c:\\skitaid\\etc\\servers-enabled\\example.conf")
	else:
		mkdir ("c:\\skitaid\\etc\\servers-available")
		shutil.copyfile ("skitaid/etc/skitaid/servers-enabled-nt/example.conf", "c:\\skitaid\\etc\\servers-available\\example.conf")
			
	data_files = [
		("c:\\skitaid\\etc\\certifications", ["skitaid/etc/skitaid/certifications/README.txt", "skitaid/etc/skitaid/certifications/example.pem", "skitaid/etc/skitaid/certifications/example.key"]),
		("c:\\skitaid\\etc\\servers-available", ["skitaid/etc/skitaid/servers-available/README.txt"]),
		("c:\\skitaid\\bin", ["skitaid/bin/install_win32_service.py", "skitaid/bin/skitaid.py", "skitaid/bin/skitaid-instance.py", "skitaid/bin/skitaid-smtpda.py", "skitaid/bin/skitaid-cron.py"]),
		(
			"c:\\skitaid\\wsgi\\example", examples	
		),
		("c:\\skitaid\\wsgi\\example\\static", ["skitaid/wsgi/example/static/reindeer.jpg"]),
		("c:\\skitaid\\wsgi\\example\\resources", ["skitaid/wsgi/example/resources/sqlite3.db"]),
		("c:\\skitaid\\wsgi\\example\\apppackages", apppackages),
		("c:\\skitaid\\wsgi\\example\\templates", templates)		
	]
	
else:
	if not os.path.isfile ("/etc/skitaid/skitaid.conf"):
		mkdir ("/etc/skitaid/servers-enabled")
		shutil.copyfile ("skitaid/etc/skitaid/skitaid.conf", "/etc/skitaid/skitaid.conf")
		shutil.copyfile ("skitaid/etc/skitaid/servers-enabled-posix/example.conf", "/etc/skitaid/servers-enabled/example.conf")
	else:
		mkdir ("/etc/skitaid/servers-available")
		shutil.copyfile ("skitaid/etc/skitaid/servers-enabled-posix/example.conf", "/etc/skitaid/servers-available/example.conf")	
		
	for fn in ["skitaid.py", "skitaid-instance.py", "skitaid-smtpda.py", "skitaid-cron.py"]:
		source = os.path.join ("skitaid/bin/", fn)
		target = os.path.join ("/usr/local/bin", fn)
		
		exists_python = "#!/usr/bin/python%s\n" % sys.version_info [0]		
		exists_python = exists_python.encode ("utf8")
		
		with open (source, "rb") as f:
			source_python = f.readline ()				
			data = f.read ()			
		with open (target, "wb") as f:
			f.write (exists_python)
			f.write (data)
		os.chmod (target, 0o755)
		
	os.chmod ("skitaid/etc/init.d/skitaid", 0o755)			
	data_files = [		
		("/etc/skitaid/certifications", ["skitaid/etc/skitaid/certifications/README.txt", "skitaid/etc/skitaid/certifications/example.pem", "skitaid/etc/skitaid/certifications/example.key"]),
		("/etc/skitaid/servers-available", ["skitaid/etc/skitaid/servers-available/README.txt"]),		
		("/var/wsgi/example", examples),
		("/var/wsgi/example/static", ["skitaid/wsgi/example/static/reindeer.jpg"]),
		("/var/wsgi/example/resources", ["skitaid/wsgi/example/resources/sqlite3.db"]),
		("/var/wsgi/example/apppackages", apppackages),
		("/var/wsgi/example/templates", templates),
		("/etc/init.d", ["skitaid/etc/init.d/skitaid"])		
	]
	

if not os.path.isdir ("skitaid"):
	new_data_files = []
	for target, files in data_files:
		newfiles = []
		for each in files:
			newfiles.append (os.path.join (python_package_dir, each))
		new_data_files.append ((target, newfiles))
	data_files = new_data_files

with open('skitaid/__init__.py', 'r') as fd:
	version = re.search(r'^__version__\s*=\s*"(.*?)"',fd.read(), re.M).group(1)
		
setup(
	name='skitaid',
	version=version,
	description='Skitai App Engine Daemon',	
	url = 'https://gitlab.com/hansroh/skitaid',
	author='Hans Roh',
	author_email='hansroh@gmail.com',	
	packages=packages,
	package_dir=package_dir,
	data_files = data_files,
	package_data = package_data,
	license='BSD',
	platforms = ["posix", "nt"],
	download_url = "https://pypi.python.org/pypi/skitaid",
	install_requires = ["skitai>=0.24.3"],
	classifiers=classifiers
)

