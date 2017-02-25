from fabric.api import *
from fabric.contrib.files import sed, exists, upload_template, append
from colors import red, bold
from importlib import import_module
import tempfile, sys, os, urlparse, fnmatch

""" Environment keys:
install_key - True/False/string, copy and install the default id_rsa.pub ssh key or specified key
packages - override of the standard packages to install on setup
pip_packages - override of the standard pip packages to install on setup
nginx_settings - dict of settings to override global settings in /etc/nginx/nginx.conf, to be placed in /etc/nginx/conf.d/fabric.conf, e.g. {'http': {...}}
geoip - True/False, install and setup geoip for django
mysql_server - True/False, install and setup server as a mysql server
mysql_settings - dict of settings to override global settings in /etc/mysql/my.cnf, to be placed in /etc/mysql/conf.d/fabric.cnf, e.g. { 'mysqld': {'bind-address': '0.0.0.0'}}
postgresql_client - True/False, install and setup django as a postgresql client
postgresql_server - True/False, install and setup server as a postgresql server
postgresql_settings - dict of settings to add/override for the postgresql server, to be placed in /etc/postgresql/9.1/main/fabric.conf
geo_django - True/False, install and setup postgresql client/servers with geo capabilities
memcached_server - True/False/dict of settings to edit into /etc/memcached.conf, e.g. {'-M': None, '-c': '1024'}
redis_server - True/False/dict of settings to edit into /etc/redis.conf, e.g. {}
database_only - True/False, this server is a database server only (mysql, memcached, etc..) no django
project - name of the project, for use in the filesystem, should only be one project even with multiple sites
sites - array of dict settings for running multiple sites, with the following keys, these settings may also optionally can be specified on the root level if only one site
{
	site - domain of the server, used to setup nginx if ALLOWED_HOSTS is not set in the settings and is used as a key when choosing a site
	ssl_cert - ssl certificate to use
	ssl_cert_key - private key to go with the cert, both must be given
	ssl_only - if True, will configure nginx to redirect all port 80 traffic to https
	local_tests - list of django tests to run locally before a deploy
	remote_tests - list of django tests to run remotely after a deploy
	settings_module - the settings module to use on deploy etc.. (DJANGO_SETTINGS_MODULE), required
	crontab - list of jobs to add to the crontab for this site, each job is (m, h, dom, moy, dow, command)
	default - if True, this will be the default nginx site
	nginx_settings - dictionary of settings to set in the / location for this site
	custom_locations - array of custom location directives to add to the nginx site configuration
	static_inside_project - if True, static and media roots will remain inside the project when fixing their paths for the server. Otherwise media and static will go into /srv/www/media and /srv/www/static
	*project - automatically copied from env['project']
	webapp_bucket - the bucket to deploy to, does not configure the bucket itself.
	webapp_files - array of static files that the webapp uses that are not under the webapp directory, specified as relative static paths that can be passed to the findstatic command e.g. js/script.js
		A better way to get extra files is to symbolically link the shared directories into the webapp project, and if using gulp only match the required files when building
		Try to NOT use this.
	webapp_clear - clear the destination path in the bucket before deploying
	webapp_gzip_types - gzip webapp files of these types. Don't specify images and PDFs because they are already compressed (see GZIP_CONTENT_TYPES) (https://developer.yahoo.com/performance/rules.html)
	webapp_cache_control - Set the Cache-Control for the file patterns specified (uses fnmatch). For no caching, use NO_CACHE, for permanent caching use PERMANENT_CACHE. For versioned files, e.g. bundle.103GA74.css use permanent caching.
}
"""

""" Requirements:
These tasks expect media to be located at project/media and static to be at project/static 
"""

""" Notes:
memcached wouldn't restart properly without setting pty=False, so all calls to service have pty=False
"""

""" TODO:
mysql queries to run on setup, such as those required for opening up to allow clients.
http://www.thegeekstuff.com/2010/08/allow-mysql-client-connection/
"""

# Dictionary of environments set from the fab file.
environments = {}
# Like env, a site that should be used when running a few of the commands.
site = None

nginx_user = 'www-data'
postgresql_user = 'postgres'

# Standard packages, (includes sqlite, mysql, memcached client setup as standard along with boto for AWS)
basic_packages = ('gcc', 'make', 'linux-headers-$(uname -r)', 'build-essential', 'libtool', 'git', 'autoconf', 'zip')
standard_packages = basic_packages + ('nginx-full', 'uwsgi', 'uwsgi-plugin-python', 'python-pip', 'python-dev', 'sqlite3', 'mysql-client', 'libmysqlclient-dev')
pil_packages = ('libjpeg-dev', 'libpng-dev', 'libfreetype6-dev')
django_pip_packages = ('django', 'south', 'django-storages', 'boto', 'distribute', 'mysql-python', 'python-memcached')
pil_pip_packages = ('pil',)
celery_pip_packages = ('celery', 'kombu', 'django-celery')
facebook_pip_packages = ('facebook-sdk',)
facebook_django_pip_packages = ('git+git://github.com/pythonforfacebook/django-facebook.git#egg=django-facebook',)

# Default settings
memcached_settings = {'-d': None, 'logfile': '/var/log/memcached.log', '-m': '64', '-p': '11211', '-u': 'memcache', '-l': '127.0.0.1'}
redis_settings = {}

GZIP_CONTENT_TYPES = ('text/css','application/javascript','application/x-javascript')
NO_CACHE = 'no-cache'
PERMANENT_CACHE = 'max-age=315360000'

# Helper functions

def __get_domain(url):
	return urlparse.urlparse(url).netloc

def __get_path(url):
	return urlparse.urlparse(url).path

def __fix_static_path(path, site):
	""" Changes a relative path (os.path.abspath('.')) that may have been specified in the settings. """
	if path.startswith(os.path.abspath('.')):
		if site.get('static_inside_project', False):
			return path.replace(os.path.abspath('.'), '/srv/www/%s' % env['project'], 1)
		else:
			return path.replace(os.path.abspath('.'), '/srv/www', 1)
	return path

def __fix_webapp_path(path):
	""" Like __fix_static_path, but webapps should always stay inside the project. """
	if path.startswith(os.path.abspath('.')):
		return path.replace(os.path.abspath('.'), '/srv/www/%s' % env['project'], 1)
	return path

def __slash_wrap(path):
	if path.startswith('/'):
		if path.endswith('/'):
			return path
		else:
			return path + '/'
	else:
		if path.endswith('/'):
			return '/' + path
		else:
			return '/%s/' % path

def __setup_aws_access_key(site):
	try:
		module = import_module(site['settings_module'])
		# Boto variables
		os.environ.setdefault("AWS_ACCESS_KEY_ID", module.AWS_ACCESS_KEY_ID)
		os.environ.setdefault("AWS_SECRET_ACCESS_KEY", module.AWS_SECRET_ACCESS_KEY)
	except:
		print red('Error: Could not access AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY from settings.', True)
		exit(1)

def __upload_to_s3(site, bucket, directory=None, files=None, prefix=None):
	""" Uploads files to an s3 bucket. Upload either an entire directory with files=None, or specific files with and optional directory prefix. """
	if bucket is None:
		print red('Error: Bucket must be specified.', True)
		return
	if directory is None and files is None:
		print red('Error: Directory and/or files must be specified.', True)
		return
	# Setup boto
	import boto
	from boto.s3.bucket import Bucket
	from boto.s3.key import Key
	import mimetypes

	__setup_aws_access_key(site)

	# Connect to S3
	c = boto.connect_s3()
	b = Bucket(c, bucket)

	# Fix the prefix
	# prefix itself shouldn't have a / prefix itself but should end with /
	if prefix:
		prefix = prefix.lstrip('/')
		if prefix and not prefix.endswith('/'):
			prefix = prefix + '/'

	def __upload(key, filename):
		k = Key(b)
		k.key = key
		headers = {}
		content_type = mimetypes.guess_type(filename)[0]
		if site.has_key('webapp_cache_control'):
			for pattern in site['webapp_cache_control']:
				if fnmatch.fnmatch(filename, pattern):
					headers['Cache-Control'] = site['webapp_cache_control'][pattern]
					break
		if site.has_key('webapp_gzip_types') and content_type in site['webapp_gzip_types']:
			from gzip import GzipFile
			from StringIO import StringIO
			# Need to specify content_type when uploading from a string!
			headers['Content-Type'] = content_type
			headers['Content-Encoding'] = 'gzip'
			s = StringIO()
			g = GzipFile(fileobj=s, mode='wb')
			with open(filename, 'rb') as f:
				g.write(f.read())
			g.close()
			k.set_contents_from_string(s.getvalue(), headers)
		else:
			k.set_contents_from_filename(filename, headers)

	if files:
		# Upload individual files
		if directory:
			keys = [filename.lstrip('/') for filename in files]
			files = [os.path.join(directory, filename) for filename in files]
		else:
			keys = [os.path.split(filename)[1] for filename in files]
		for i, filename in enumerate(files):
			print 'Uploading ', keys[i]
			if prefix:
				key = prefix + keys[i]
			else:
				key = keys[i]
			__upload(key, filename)
	elif directory:
		# Upload an entire directory
		def __upload_dir(arg, dirname, names):
			# arg is the starting directory
			for name in names:
				filename = os.path.join(dirname, name)
				if not os.path.isdir(filename) and not os.path.islink(filename) and not name.startswith('.'):
					key = filename[len(arg):]
					if key.startswith('/'):
						key = key[1:]
					if prefix:
						key = prefix + key
					print 'Uploading ', key
					__upload(key, filename)
		os.path.walk(directory, __upload_dir, directory)

def __delete_from_s3(site, bucket, prefix=None):
	""" Remove all files with the prefix specified from the bucket. """
	if bucket is None:
		print red('Error: Bucket must be specified.', True)
		return
	# Setup boto
	import boto
	from boto.s3.bucket import Bucket
	from boto.s3.key import Key

	__setup_aws_access_key(site)

	# Fix the prefix
	if prefix:
		prefix = prefix.lstrip('/')

	# Connect to S3, list the contents, and remove all of the keys
	c = boto.connect_s3()
	b = Bucket(c, bucket)
	result_set = b.list(prefix=prefix)
	result = b.delete_keys([key.name for key in result_set])

# Package functions

def __apt_get_install(packages=standard_packages, update=True):
	if update:
		sudo('apt-get update -y')
	for package in packages:
		sudo('apt-get install %s -y' % package)

def __pip_install(packages=django_pip_packages, upgrade=True):
	if upgrade:
		sudo('pip install --upgrade pip')
		sudo('pip install --upgrade distribute')
	if 'pil' in packages:
		# http://stackoverflow.com/questions/7648200/pip-install-pil-e-tickets-1-no-jpeg-png-support
		with settings(warn_only=True):
			if exists('/usr/lib/x86_64-linux-gnu/libfreetype.so'):
				sudo('ln -s /usr/lib/x86_64-linux-gnu/libfreetype.so /usr/lib/libfreetype.so')
			if exists('/usr/lib/x86_64-linux-gnu/libz.so'):
				sudo('ln -s /usr/lib/x86_64-linux-gnu/libz.so /usr/lib/libz.so')
			if exists('/usr/lib/x86_64-linux-gnu/libjpeg.so'):
				sudo('ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib/libjpeg.so')
	for package in packages:
		sudo('pip install %s' % package)

def __install_geoip():
	""" Install geoip (convert ip addresses into locations). """
	if not exists('/usr/local/geoip'):
		__apt_get_install(('libgeoip1',), False)
		run('wget --no-clobber http://www.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz')
		run('gunzip GeoLiteCity.dat.gz')
		sudo('mkdir /usr/local/geoip')
		sudo('mv GeoLiteCity.dat /usr/local/geoip/')

def __create_postgresql_database_template_old():
	# Create the database template
	run('wget --no-clobber https://docs.djangoproject.com/en/dev/_downloads/create_template_postgis-1.5.sh')
	run('chmod 755 create_template_postgis-1.5.sh')
	sudo('su postgres -c ./create_template_postgis-1.5.sh')

def __install_postgis(old=False):
	__apt_get_install(('postgresql-server-dev-all', 'libpq-dev', 'libxml2', 'libxml2-dev'), False)

	# Install geos
	run('wget --no-clobber http://archive.ubuntu.com/ubuntu/pool/universe/g/geos/geos_3.3.3.orig.tar.gz')
	run('tar -xzf geos_3.3.3.orig.tar.gz')
	with cd('geos-3.3.3'):
		run('./configure')
		run('make')
		sudo('make install')

	# Install proj.4
	# https://docs.djangoproject.com/en/dev/ref/contrib/gis/install/
	run('wget --no-clobber http://download.osgeo.org/proj/proj-4.8.0.tar.gz')
	run('wget --no-clobber http://download.osgeo.org/proj/proj-datumgrid-1.5.tar.gz')
	run('tar -xzf proj-4.8.0.tar.gz')
	with cd('proj-4.8.0/nad'):
		run('tar -xzf ../../proj-datumgrid-1.5.tar.gz')
		with cd('..'):
			run('./configure')
			run('make')
			sudo('make install')

	# Install gdal
	run('wget --no-clobber http://download.osgeo.org/gdal/gdal-1.9.2.tar.gz')
	run('tar -xzf gdal-1.9.2.tar.gz')
	with cd('gdal-1.9.2'):
		run('./configure')
		run('make')
		sudo('make install')
		sudo('ldconfig')

	if old:
		run('wget --no-clobber http://postgis.refractions.net/download/postgis-1.5.5.tar.gz')
		run('tar -xzf postgis-1.5.5.tar.gz')
		with cd('postgis-1.5.5'):
			run('./configure')
			run('make')
			sudo('make install')
	else:
		run('wget --no-clobber http://download.osgeo.org/postgis/source/postgis-2.0.3.tar.gz')
		run('tar -xzf postgis-2.0.3.tar.gz')
		with cd('postgis-2.0.3'):
			run('./configure')
			run('make')
			sudo('make install')

def __setup_postgresql_database():
	# Create the user for django to access the database with
	for site in env['sites']:
		with settings(warn_only=True):
			module = import_module(site['settings_module'])
			DATABASES = module.DATABASES
			sudo('createuser --createdb --no-superuser --no-createrole %s' % DATABASES['default']['USER'], user=postgresql_user)
			sudo("psql -c \"ALTER USER %s WITH PASSWORD '%s';\"" % (DATABASES['default']['USER'], DATABASES['default']['PASSWORD']), user=postgresql_user)
			sudo('createuser --createdb --no-superuser --no-createrole %s' % env.user, user=postgresql_user)
			sudo('dropdb %s' % DATABASES['default']['NAME'], user=postgresql_user)
		sudo('createdb %s' % DATABASES['default']['NAME'], user=postgresql_user)
		if env.has_key('geo_django') and env['geo_django']:
			sudo("psql %s -c 'CREATE EXTENSION postgis;'" % DATABASES['default']['NAME'], user=postgresql_user)
			sudo("psql %s -c 'CREATE EXTENSION postgis_topology;'" % DATABASES['default']['NAME'], user=postgresql_user)
			# http://tmbu.blogspot.com/2012/11/postgres-postgis-django-os-x-and.html
			# http://stackoverflow.com/questions/4737982/django-avoids-creating-pointfield-in-the-database-when-i-run-python-manage-py-sy
			sudo("psql %s -c 'GRANT ALL PRIVILEGES ON geometry_columns TO %s;'" % (DATABASES['default']['NAME'], DATABASES['default']['USER']), user=postgresql_user)
			sudo("psql %s -c 'GRANT ALL PRIVILEGES ON spatial_ref_sys TO %s;'" % (DATABASES['default']['NAME'], DATABASES['default']['USER']), user=postgresql_user)
			# old
			#run('createdb -T template_postgis %s' % DATABASES['default']['NAME'])

def __setup_postgresql_settings():
	if env.has_key('postgresql_settings'):
		with tempfile.NamedTemporaryFile('w') as f:
			for setting in env['postgresql_settings']:
				f.write('%s = %s\n' % (setting, env['postgresql_settings'][setting]))
			f.flush()
			put(f.name, '/etc/postgresql/9.1/main/fabric.conf', use_sudo=True, mode=0644)
			sudo('chown %s:%s /etc/postgresql/9.1/main/fabric.conf' % (postgresql_user, postgresql_user))
			append('/etc/postgresql/9.1/main/postgresql.conf', "\n\ninclude 'fabric.conf'\n", use_sudo=True)
		sudo('service postgresql restart', pty=False)

def __setup_postgresql_server():
	""" Setup and install postgresql. """
	__apt_get_install(('postgresql',), False)
	if env.has_key('geo_django') and env['geo_django']:
		__install_postgis()
		#__create_postgresql_database_template_old()
	__setup_postgresql_database()
	__setup_postgresql_settings()

def __setup_postgresql_client():
	if env.has_key('geo_django') and env['geo_django'] and not (env.has_key('postgresql_server') and env['postgresql_server']):
		# Install PostGIS
		__install_postgis()
	# Install python postgresql support
	__apt_get_install(('python-dev', 'postgresql-server-dev-all'), False)
	__pip_install(('psycopg2',), False)

def __setup_mysql_settings():
	if env.has_key('mysql_settings'):
		with tempfile.NamedTemporaryFile('w') as f:
			for section in env['mysql_settings']:
				f.write('[%s]\n' % section)
				for setting in env['mysql_settings'][section]:
					f.write('%s = %s\n' % (setting, env['mysql_settings'][section][setting]))
			f.flush()
			put(f.name, '/etc/mysql/conf.d/fabric.cnf', use_sudo=True, mode=0644)		
			sudo('chown root:root /etc/mysql/conf.d/fabric.cnf')
		sudo('service mysql restart', pty=False)

def __setup_mysql():
	""" Install and setup mysql. """
	__apt_get_install(('mysql-server',), False)
	__setup_mysql_settings()
	# TODO: setup user, database etc... here

def __configure_memcached():
	if env.has_key('memcached_server') and type(env['memcached_server']) is dict:
		with tempfile.NamedTemporaryFile('w') as f:
			for setting in env['memcached_server']:
				if env['memcached_server'][setting]:
					f.write('%s %s\n' % (setting, env['memcached_server'][setting]))
				else:
					f.write('%s\n' % setting)
			f.flush()
			put(f.name, '/etc/memcached.conf', use_sudo=True, mode=0644)
			sudo('chown root:root /etc/memcached.conf')
		sudo('service memcached restart', pty=False)

def __setup_memcached():
	""" Install and setup memcached. """
	__apt_get_install(('memcached',), False)
	__configure_memcached()

def __configure_redis():
	if env.has_key('redis_server') and type(env['redis_server']) is dict:
		with tempfile.NamedTemporaryFile('w') as f:
			for setting in env['redis_server']:
				if env['redis_server'][setting]:
					f.write('%s %s\n' % (setting, env['redis_server'][setting]))
				else:
					f.write('%s\n' % setting)
			f.flush()
			put(f.name, '/etc/redis/fabric.conf', use_sudo=True, mode=0644)
			sudo('chown root:root /etc/redis/fabric.conf')
			append('/etc/redis/redis.conf', 'include fabric.conf', use_sudo=True)
		sudo('service redis-server restart', pty=False)

def __setup_redis():
	""" Install and setup memcached. """
	__apt_get_install(('redis-server',), False)
	__configure_redis()

NGINX_SSL = """listen 443 ssl;\n\tssl_certificate %s;\n\tssl_certificate_key %s;"""
NGINX_LOCATION = """location %s {\n\t\talias %s;\n\t\texpires 1d;\n\t}"""
NGINX_LOCATION_DOMAIN = """location %s {\n\t\trewrite ^(.*)$ http://%s$1 permanent;\n\t}"""
NGINX_WEBAPP_LOCATION = """location %s {\n\t\talias %s;\n\t\ttry_files $uri $uri/%s %s;\n\t}"""

def __setup_nginx():
	""" Run the nginx setup for all sites. """
	# Write new settings
	if env.has_key('nginx_settings') and type(env['nginx_settings']) is dict:
		with tempfile.NamedTemporaryFile('w') as f:
			for section in env['nginx_settings']:
				if type(env['nginx_settings'][section]) is dict:
					f.write('%s {\n' % section)
					for setting in env['nginx_settings'][section]:
						f.write('%s %s;\n' % (setting, env['nginx_settings'][section][setting]))
					f.write('}\n')
				elif type(env['nginx_settings'][section]) is bool:
					f.write('%s %s;\n' % (setting, 'on' if env['nginx_settings'][section] else 'off'))
				else:
					f.write('%s %s;\n' % (setting, str(env['nginx_settings'][section])))
			f.flush()
			put(f.name, '/etc/nginx/conf.d/fabric.conf', use_sudo=True, mode=0644)		
			sudo('chown root:root /etc/nginx/conf.d/fabric.conf')

	# Write the site settings
	for site in env['sites']:
		if site.has_key('default') and site['default']:
			site['default_str'] = ' default_server'
		else:
			site['default_str'] = ''
		if site.has_key('ssl_cert') and site.has_key('ssl_cert_key') and site['ssl_cert'] and site['ssl_cert_key']:
			site['ssl_str'] = NGINX_SSL % (site['ssl_cert'], site['ssl_cert_key'])
		else:
			site['ssl_str'] = ''
		module = import_module(site['settings_module'])
		if module.ALLOWED_HOSTS:
			site['allowed_hosts'] = ' '.join(module.ALLOWED_HOSTS)
		else:
			site['allowed_hosts'] = site['site']
		# Setup the static and media locations
		locations = []
		domain = __get_domain(module.STATIC_URL)
		if domain:
			locations.append(NGINX_LOCATION_DOMAIN % (__slash_wrap(__get_path(module.STATIC_URL)), domain))
		else:
			locations.append(NGINX_LOCATION % (__slash_wrap(module.STATIC_URL), __fix_static_path(module.STATIC_ROOT, site)))
		domain = __get_domain(module.MEDIA_URL)
		if domain:
			locations.append(NGINX_LOCATION_DOMAIN % (__slash_wrap(__get_path(module.MEDIA_URL)), domain))
		else:
			locations.append(NGINX_LOCATION % (__slash_wrap(module.MEDIA_URL), __fix_static_path(module.MEDIA_ROOT, site)))
		# Add any custom locations
		if site.has_key('custom_locations'):
			if isinstance(site['custom_locations'], (tuple, list)):
				for location in site['custom_locations']:
					locations.append(location)
			else:
				locations.append(site['custom_locations'])
		site['static_locations'] = '\n\n\t'.join(locations)
		if site.has_key('nginx_settings') and type(site['nginx_settings']) is dict:
			site['nginx_settings_str'] = '\n\t\t'.join(['%s %s;' % (setting, site['nginx_settings'][setting]) for setting in site['nginx_settings']])
		else:
			site['nginx_settings_str'] = ''
		# Configure the webapp if necessary
		webapp_root = getattr(module, 'WEBAPP_ROOT', None)
		webapp_url = __slash_wrap(getattr(module, 'WEBAPP_URL', '/'))
		if webapp_root:
			webapp_root = __fix_webapp_path(webapp_root)
			webapp_index = getattr(module, 'WEBAPP_INDEX', 'index.html')
			if webapp_url == '/':
				site['app_location'] = '@%s-app' % site['site'].replace('.', '-')
				site['webapp_location'] = NGINX_WEBAPP_LOCATION % (webapp_url, webapp_root, webapp_index, site['app_location'])
			else:
				site['app_location'] = '/'
				site['webapp_location'] = NGINX_WEBAPP_LOCATION % (webapp_url, webapp_root, webapp_index, '=404')
			# Configure the 404 file if available
			if os.path.isfile(os.path.join(module.WEBAPP_ROOT, '404.html')):
				site['webapp_404'] = 'error_page 404 %s404.html;' % webapp_url
			else:
				site['webapp_404'] = ''
		else:
			site['app_location'] = '/'
			site['webapp_location'] = ''
			site['webapp_404'] = ''
		if site.has_key('ssl_only') and site['ssl_only']:
			nginx_template = '%s/templates/nginx-site-https.conf' % os.path.dirname(__file__)
		else:
			nginx_template = '%s/templates/nginx-site.conf' % os.path.dirname(__file__)
		upload_template(nginx_template, '/etc/nginx/sites-available/%s.conf' % site['site'], context=site, use_sudo=True, mode=0644)
		sudo('chown root:root /etc/nginx/sites-available/%s.conf' % site['site'])
		with settings(warn_only=True):
			sudo('ln -s /etc/nginx/sites-available/%s.conf /etc/nginx/sites-enabled/%s.conf' % (site['site'], site['site']))
	sudo('service nginx restart', pty=False)

def __setup_uwsgi():
	""" Run the uwsgi setup for all sites. """
	for site in env['sites']:
		upload_template('%s/templates/uwsgi-app.ini' % os.path.dirname(__file__), '/etc/uwsgi/apps-available/%s.ini' % site['site'], context=site, use_sudo=True, mode=0644)
		with settings(warn_only=True):
			sudo('ln -s /etc/uwsgi/apps-available/%s.ini /etc/uwsgi/apps-enabled/%s.ini' % (site['site'], site['site']))
	sudo('service uwsgi restart', pty=False)

def create_public_bucket_policy(bucket_name):
	import json
	policy = {
		"Version": "2008-10-17",
		"Statement": [
			{
				"Sid": "AddPerm",
				"Effect": "Allow",
				"Principal": {
					"AWS": "*"
				},
				"Action": "s3:GetObject",
				"Resource": "arn:aws:s3:::%s/*" % bucket_name
			}
		]
	}
	return json.dumps(policy)

DEFAULT_CORS_RULE = {'allowed_method': ['GET'], 'allowed_origin': ['*'], 'allowed_header': ['Authorization'], 'max_age_seconds': 3000}

def __setup_buckets():
	""" Setup buckets on S3. If site is not specified, then the command will be run on all sites. """
	global site
	if not site:
		for site in env['sites']:
			if site.has_key('buckets'):
				__setup_buckets()
		site = None
		return

	__setup_aws_access_key(site)

	from boto import connect_s3
	from boto.s3.bucket import Bucket
	from boto.s3.key import Key

	for bucket_config in site['buckets']:
		# Connect and make sure the bucket exists
		print bold(u'Configuring bucket %s...' % bucket_config['name'])
		connection = connect_s3()
		try:
			bucket = connection.get_bucket(bucket_config['name'])
		except:
			connection.create_bucket(bucket_config['name'])
		# Set the bucket policy
		if bucket_config.has_key('policy'):
			bucket.set_policy(bucket_config['policy'])
		# Setup CORS, array of rules
		# http://boto.readthedocs.org/en/latest/ref/s3.html#boto.s3.cors.CORSConfiguration
		if bucket_config.has_key('cors') and bucket_config['cors'] is None:
			# If explicity set to None, then remove the cors policy
			bucket.delete_cors()
		else:
			if not bucket_config.has_key('cors'):
				# If not specified, use the default GET policy
				bucket_config['cors'] = (DEFAULT_CORS_RULE,)
			from boto.s3.cors import CORSConfiguration
			cors_config = CORSConfiguration()
			for rule in bucket_config['cors']:
				cors_config.add_rule(**rule)
			bucket.set_cors(cors_config)
		# Setup the lifecycle, array of rules
		# http://boto.readthedocs.org/en/latest/ref/s3.html#boto.s3.lifecycle.Lifecycle
		if bucket_config.has_key('lifecycle'):
			from boto.s3.lifecycle import Lifecycle
			lifecycle_config = Lifecycle()
			for rule in bucket_config['lifecycle']:
				lifecycle_config.add_rule(**rule)
			bucket.configure_lifecycle(lifecycle_config)
		else:
			bucket.delete_lifecycle_configuration()
		# Setup the bucket website hosting {suffix, error_key, routing_rules, redirect_all_requests_to}
		# http://boto.readthedocs.org/en/latest/ref/s3.html
		# https://github.com/boto/boto/blob/develop/boto/s3/website.py
		if bucket_config.has_key('website'):
			# Expand the routing rules, array of {condition, redirect}
			if bucket_config['website'].has_key('routing_rules'):
				from boto.s3.website import RoutingRules, RoutingRule
				routing_rules = RoutingRules()
				for rule in bucket_config['website']['routing_rules']:
					routing_rules.add_rule(RoutingRule(**rule))
				bucket_config['website']['routing_rules'] = routing_rules
			# Expand the redirect, redirect_all_requests_to is {hostname, protocol}
			if bucket_config['website'].has_key('redirect_all_requests_to'):
				from boto.s3.website import RedirectLocation
				bucket_config['website']['redirect_all_requests_to'] = RedirectLocation(**bucket_config['website']['redirect_all_requests_to'])
			bucket.configure_website(**bucket_config['website'])
		else:
			bucket.delete_website_configuration()

def __generate_s3_ajax():
	""" Generate jquery ajax code for saving files with the S3 policy documents. A site must be specified. """
	# http://aws.amazon.com/articles/1434
	# http://docs.aws.amazon.com/AmazonS3/2006-03-01/dev/HTTPPOSTForms.html
	global site
	if not site:
		print red('Error: An environment and site must both first be specified.')
		exit(1)
	module = import_module(site['settings_module'])
	from django.conf import settings
	from django.template import Template, Context
	import json, hmac, hashlib, base64
	settings.configure()
	with open('%s/templates/s3-ajax.js' % os.path.dirname(__file__)) as f:
		template = Template(f.read())
	context = {'access_key_id': module.AWS_ACCESS_KEY_ID, 'secret_access_key': module.AWS_SECRET_ACCESS_KEY, 'policies': []}
	policy_context_vars = ('success_action_redirect', 'bucket', 'acl')
	for name, policy in site['policy_documents'].items():
		policy_str = json.dumps(policy)
		policy['headers'] = {}
		# Process the conditions
		for condition in policy['conditions']:
			if type(condition) is dict:
				key = condition.keys()[0]
				value = condition.values()[0]
			elif type(condition) in (list, tuple):
				# The first value will always be starts-with or eq but they are treated the same
				if condition[0] not in ('starts-with', 'eq'):
					continue
				key = condition[1][1:]
				value = condition[2]
				if key == 'key':
					policy['directory'] = value
					continue
			if key in policy_context_vars:
				policy[key] = value
			elif key == 'Expires' or key.startswith('Content-'):
				policy['headers'][key] = value
		policy['name'] = name
		policy['encoded'] = base64.b64encode(policy_str)
		policy['signature'] = base64.b64encode(hmac.new(module.AWS_SECRET_ACCESS_KEY, policy_str, hashlib.sha1).digest())
		context['policies'].append(policy)
	print template.render(Context(context, autoescape=False))

def __set_environment(e):
	env.update(e)
	# Ensure that the sites array exists
	if not env.has_key('sites') or not env['sites']:
		env['sites'] = [dict(env)]
	# Copy the project name into each of the sites
	for site in env['sites']:
		site['project'] = env['project']

def set_default_environment(e):
	for arg in sys.argv:
		if arg.startswith('e:'):
			return
	__set_environment(environments[e])

# Common tasks

@task
def e(name):
	""" Set the environment for use with other commands. """
	if name and name.lower() in environments.keys():
		__set_environment(environments[name.lower()])
	else:
		print "Error: Unknown environment specified."

@task
def s(name):
	""" Set the site to use with other commands. Currently: manage and deploywebapp """
	global site
	if not env.has_key('sites'):
		print red('Error: An environment must first be specified.')
		exit(1)
	for s in env['sites']:
		if s['site'].lower().find(name.lower()) != -1:
			site = s
			break
		s = None

@task
def setup():
	""" Setup a server from scratch. """

	# Copy an ssh key to login later
	if env.has_key('install_key') and env['install_key']:
		with settings(warn_only=True):
			run('mkdir -p .ssh')
			if type(env['install_key']) is bool:
				put('~/.ssh/id_rsa.pub', '.ssh/authorized_keys')
			else:
				put('~/.ssh/%s' % env['install_key'], '.ssh/authorized_keys')

	if not env.has_key('database_only') or not env['database_only']:
		# Install packages
		if env.has_key('packages'):
			__apt_get_install(env['packages'])
		else:
			__apt_get_install()
		
		# Install pip packages
		if env.has_key('pip_packages'):
			__pip_install(env['pip_packages'])
		else:
			__pip_install()

		# Setup the web server
		__setup_nginx()
		__setup_uwsgi()

		# Install geoip library/data
		if env.has_key('geoip') and env['geoip']:
			__install_geoip()
	else:
		# Only a database server, make sure packages are up to date and install the basics
		sudo('apt-get update -y')
		if env.has_key('packages'):
			__apt_get_install(env['packages'])
		else:
			__apt_get_install(basic_packages)

	if env.has_key('mysql_server') and env['mysql_server']:
		__setup_mysql()

	if env.has_key('postgresql_server') and env['postgresql_server']:
		__setup_postgresql_server()

	if env.has_key('memcached_server') and env['memcached_server'] is not False:
		__setup_memcached()

	if env.has_key('postgresql_client') and env['postgresql_client']:
		__setup_postgresql_client()

@task
def upgrade():
	""" Upgrade a server's packages. """
	sudo('apt-get upgrade -y')
	if env.has_key('pip_packages'):
		packages = env['pip_packages']
	else:
		packages = django_pip_packages
	for package in packages:
		sudo('pip install --upgrade %s' % package)

@task
def restart():
	""" Restarts nginx and uWSGI. """
	sudo('service uwsgi restart')
	sudo('service nginx restart')

@task
def manage(*args):
	""" Run a management command using the supplied arguments. If site is not specified command will be run on all sites. """

	if site is not None:
		with cd('/srv/www/%s' % site['project']):
			sudo('python manage.py %s --settings %s' % (' '.join(args), site['settings_module']), user=nginx_user)
	else:
		for site in env['sites']:
			with cd('/srv/www/%s' % site['project']):
				sudo('python manage.py %s --settings %s' % (' '.join(args), site['settings_module']), user=nginx_user)

class own_project(object):
	""" Changes the permissions of the project between the ssh user and nginx user. """
	def __init__(self):
		pass
	def __enter__(self):
		sudo('chown -R %s:%s /srv/www/%s' % (env['user'], env['user'], env['project']))
	def __exit__(self, *_):
		sudo('chown -R %s:%s /srv/www/%s' % (nginx_user, nginx_user, env['project']))

def __get_excluded():
	"""
	Get an excluded list of patterns.
	rsync patterns are similar to .gitignore patterns. e.g. /foo matches foo at the base.
	http://git-scm.com/docs/gitignore
	http://ss64.com/bash/rsync.html
	"""
	excluded = ['.*', '*.pyc', '*.db']
	# Exclude anything in the root .gitignore file
	if os.path.exists('.gitignore'):
		with file('.gitignore', 'r') as f:
			for line in f:
				line = line.strip()
				if line.startswith('.') or line.find('!') != -1:
					continue
				if line not in excluded:
					excluded.append(line)
	# Exlude all of the webapp's node_modules
	for site in env['sites']:
		module = import_module(site['settings_module'])
		os.environ.setdefault("DJANGO_SETTINGS_MODULE", site['settings_module'])
		if hasattr(module, 'WEBAPP_ROOT'):
			try:
				from management.commands.runwebapp import get_webapp_taskrunner
				parent, task_runner = get_webapp_taskrunner(module.WEBAPP_ROOT)
				if task_runner:
					excluded.append('/' + os.path.relpath(parent) + '/node_modules')
					excluded.append('/' + os.path.relpath(parent) + '/bower_components')
				# If wanting to exclude the entire webapp
				#if task_runner:
				#	excluded.append('/' + os.path.relpath(parent))
				#else:
				#	excluded.append('/' + os.path.relpath(module.WEBAPP_ROOT))
			except:
				print red('Warning: Could not import webapp settings for %s when syncing.' % site['site'], True)
	return excluded

SYNC_COMMAND = 'rsync -avz %s --delete --delete-excluded%s ./ %s@%s:/srv/www/%s'

def sync():
	""" Syncs the local code to the server. Used as part of the deploy process. Wrap in the task decorator to enable. sync = task(sync) """
	sudo('mkdir -p /srv/www/%s' % env['project'])
	with own_project():
		# Preserve existing media if a subdirectory of the project
		for site in env['sites']:
			module = import_module(site['settings_module'])
			MEDIA_ROOT = __fix_static_path(module.MEDIA_ROOT, site)
			if MEDIA_ROOT.startswith('/srv/www/%s/' % env['project']) and exists(MEDIA_ROOT):
				sudo('mv %s /srv/www/%smedia' % (MEDIA_ROOT, env['project']))

		# Sync and set the owner
		excluded = __get_excluded()
		excluded = ['--exclude="%s"' % ex for ex in excluded]
		local(SYNC_COMMAND % (' '.join(excluded), ' -e "ssh -i %s"' % os.path.expanduser(env['key_filename']) if env.get('key_filename') else '', env['user'], env['hosts'][0], env['project']))

		# Create the media directory
		# Restore existing media if a subdirectory of the project, if it is outside the project make sure it is owned by nginx
		for site in env['sites']:
			module = import_module(site['settings_module'])
			MEDIA_ROOT = __fix_static_path(module.MEDIA_ROOT, site)
			sudo('mkdir -p %s' % MEDIA_ROOT)
			if MEDIA_ROOT.startswith('/srv/www/%s/' % env['project']):
				if exists('/srv/www/%smedia' % env['project']):
					# Delete the media directory but leave intermediate directories then restore with a move
					sudo('rm -rf %s' % MEDIA_ROOT)
					sudo('mv /srv/www/%smedia %s' % (env['project'], MEDIA_ROOT))
			else:
				sudo('chown -R %s:%s %s' % (nginx_user, nginx_user, MEDIA_ROOT))

		# Copy any additional webapp files
		if site.has_key('webapp_files') and site['webapp_files']:
			from django.contrib.staticfiles import finders
			module = import_module(site['settings_module'])
			if hasattr(module, 'WEBAPP_ROOT'):
				WEBAPP_ROOT = __fix_webapp_path(module.WEBAPP_ROOT)
				for filename in site['webapp_files']:
					result = finders.find(filename)
					if not result:
						print red('Error: Could not find static file %s.' % filename, True)
						return
					result = result[0] if isinstance(result, (list, tuple)) else result
					put(result, os.path.join(WEBAPP_ROOT, filename), use_sudo=True, mode=0644)

def __sync_dry_run():
	""" Do an rsync dry run to see which files will be updated when deploying. """
	# e.g. To show just migrations: fab e:production x:dryrun | grep -v "^deleting" | grep -v "/$" | grep "^shared/migrations"
	excluded = __get_excluded()
	excluded = ['--exclude="%s"' % ex for ex in excluded]
	local(SYNC_COMMAND % (' '.join(excluded), ' --dry-run -e "ssh -i %s"' % os.path.expanduser(env['key_filename']) if env.get('key_filename') else '', env['user'], env['hosts'][0], env['project']))

def sync_down(path=''):
	""" Syncs down stuff from the server. Wrap in the task decorator to enable. sync_down = task(sync_down) """
	if path.startswith('/'):
		path = path[1:]
	if not path.endswith('/'):
		path += '/'
	local('rsync -avz --exclude=".*" --exclude="*.pyc" --exclude="*.sh" --exclude="*.db" %s@%s:/srv/www/%s%s ./%s' % (env['user'], env['hosts'][0], env['project'], path, path))

def __deploy_webapp():
	""" Deploy a webapp to S3 with the prefix of WEBAPP_URL. If site is not specified, then the command will be run on all sites. """
	global site
	if not site:
		for site in env['sites']:
			if site.has_key('webapp_bucket'):
				__deploy_webapp()
		site = None
		return

	try:
		module = import_module(site['settings_module'])
		root = module.WEBAPP_ROOT
		prefix = getattr(module, 'WEBAPP_URL', '/')
	except:
		print red('Error: Could not import webapp settings to deploy.', True)
		return
	# Build the webapp if needed
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", site['settings_module'])
	from management.commands.runwebapp import build_webapp
	build_webapp(root)
	# Clear the bucket
	if site.has_key('webapp_clear') and site['webapp_clear']:
		__delete_from_s3(site, site['webapp_bucket'], prefix=prefix)
	# Upload the webapp files
	__upload_to_s3(site, site['webapp_bucket'], root, prefix=prefix)
	# Upload the static files found in other directories wih the static file finder
	if site.has_key('webapp_files') and site['webapp_files']:
		from django.contrib.staticfiles import finders
		for filename in site['webapp_files']:
			result = finders.find(filename)
			if not result:
				print red('Error: Could not find static file %s.' % filename, True)
				return
			result = result[0] if isinstance(result, (list, tuple)) else result
			__upload_to_s3(site, site['webapp_bucket'], result[:-len(filename)], (filename,), prefix=prefix)

def deploy_crontab():
	""" Creates a new crontab for the nginx user. """
	# list of (5,6,'*',0,'full shell command') or just 'management command'
	# http://www.adminschoice.com/crontab-quick-reference/

	# Get the existing crontab
	result = sudo('crontab -l -u %s' % nginx_user, warn_only=True)
	if result.succeeded:
		lines = result.split('\n')
	for site in env['sites']:
		start = '# start [fabric] [%s]' % site['site']
		end = '# end [fabric] [%s]' % site['site']
		try:
			# Remove the presvious section
			start_index = lines.index(start)
			end_index = lines.index(end)
			lines = lines[0:start_index] + lines[end_index+1:]
		except:
			pass
		if site.has_key('crontab') and site['crontab']:
			lines.append(start)
			for job in site['crontab']:
				if isinstance(job, (str, unicode)):
					lines.append('0 0 * * * cd %s && python manage.py %s --settings %s >/dev/null 2>&1' % ('/srv/www/%s' % env['project'], job, site['settings_module']))
				else:
					lines.append(' '.join())
			lines.append(end)
	if lines:
		import sha
		lines = lines.join('\n')
		crontab_file = '/tmp/fabric_crontab_' + sha.new(lines).digest().encode('hex')[0:10]
		sudo('touch ' + crontab_file)
		append(crontab_file, lines)
		sudo('crontab -u %s %s' % (nginx_user, crontab_file))
		sudo('rm ' + crontab_file)
	else:
		sudo('crontab -r %s' % nginx_user, warn_only=True)

@task
def deploy(raw=False):
	""" Deploys the latest version of the code. """
	__deploy_webapp()
	for site in env['sites']:
		if site.has_key('local_tests') and site['local_tests']:
			local('python manage.py test %s --settings %s' % (' '.join(site['local_tests']), site['settings_module']))
	sudo('service uwsgi stop')
	sudo('service nginx stop')
	sync()
	with own_project():
		with cd('/srv/www/%s' % env['project']):
			for site in env['sites']:
				sudo('python manage.py syncdb --settings %s --noinput' % site['settings_module'])
				sudo('python manage.py migrate --settings %s --noinput' % site['settings_module'])
				with settings(warn_only=True):
					# The collectstatic with --clear with raise an exception and fail if the static directory does not already exist, so retry without --clear if it fails
					result = sudo('python manage.py collectstatic --settings %s --noinput --clear' % site['settings_module'])
					if result.failed:
						sudo('python manage.py collectstatic --settings %s --noinput' % site['settings_module'])
				if site.has_key('remote_tests') and site['remote_tests']:
					with settings(warn_only=True):
						sudo('python manage.py test %s --settings %s ' % (' '.join(site['remote_tests']), site['settings_module']))
	sudo('service uwsgi start')
	sudo('service nginx start')
	deploy_crontab()

@task
def reboot():
	""" Reboot the server. """
	sudo('shutdown -r now')

def __uname():
	""" Print the remote uname. """
	run('uname -a')

def __ntp():
	""" Sync the time on the host using network time. """
	sudo('ntpdate pool.ntp.org')

def __exports():
	""" Prints commands to export AWS environment variables. Example use: eval `fab --hide running,status e:production x:exports` """
	for site in env['sites']:
		try:
			module = import_module(site['settings_module'])
			# Command line interface variables
			print 'export AWS_ACCESS_KEY=%s' % module.AWS_ACCESS_KEY_ID
			print 'export AWS_SECRET_KEY=%s' % module.AWS_SECRET_ACCESS_KEY
			# Boto variables
			print 'export AWS_ACCESS_KEY_ID=%s' % module.AWS_ACCESS_KEY_ID
			print 'export AWS_SECRET_ACCESS_KEY=%s' % module.AWS_SECRET_ACCESS_KEY
		except:
			pass

# Archive functions

def git_archive():
	""" Creates a git archive with all submodules included. Uses gnutar so the archive is compatible on linux. """
	if env.has_key('project'):
		project = env['project']
	else:
		project = 'project'
	local("git archive HEAD -o %s.tar; git submodule foreach 'git archive --prefix ${path}/ HEAD -o ../temp.tar; gnutar -Af ../%s.tar ../temp.tar; rm ../temp.tar'; gzip -f %s.tar" % (project, project, project))

def git_raw_archive():
	""" Creates an archive of files not based on the git repository. For testing uncommitted code. """
	if env.has_key('project'):
		project = env['project']
	else:
		project = 'project'
	local("gnutar -cf %s.tar .; gzip -f %s.tar" % (project, project))

@task
def archive(raw=False):
	""" Creates a git archive with all submodules included. Uses gnutar so the archive is compatible on linux. Optional argument: true for a raw archive. """
	if raw:
		git_raw_archive()
	else:
		git_archive()

MYSQL_CLIENT_INSTRUCTIONS = """1. Download the connector from: http://dev.mysql.com/downloads/connector/c/
2. Install the connector into /usr/local/
3. Add the correct /usr/local/mysql-connector-c-<your version here>/bin directory to PATH
4. Add the correct /usr/local/mysql-connector-c-<your version here>/lib directory to DYLD_LIBRARY_PATH"""

MYSQL_PYTHON_INSTRUCTIONS = """1. Download MySQL-python from: https://pypi.python.org/pypi/MySQL-python
2. export CFLAGS=-Wunused-command-line-argument-hard-error-in-future
3. python setup.py build
4. sudo python setup.py install
"""

PYCRYPTO_INSTRUCTIONS = """1. Download pycrypto from: https://www.dlitz.net/software/pycrypto/
2. export CFLAGS=-Wunused-command-line-argument-hard-error-in-future
3. ./configure
4. python setup.py build
5. sudo python setup.py install
"""

def __localsetup():
	""" Installs packages necessary for a local mac setup. """
	with settings(warn_only=True):
		packages = env['pip_packages'] if env.has_key('pip_packages') else django_pip_packages
		# Check to make sure mysql client libraries are installed
		if 'mysql-python' in packages:
			result = local('which mysql_config', True)
			if not result.succeeded:
				# Print mysql client setup instructions and exit
				print red('You do not have the mysql client libraries installed.', True)
				print 'Please follow these instructions first:'
				print MYSQL_CLIENT_INSTRUCTIONS
				return

		try:
			import MySQLdb
		except:
			import platform
			if platform.system() == 'Darwin':
				print red('You do not have MySQL-python installed.', True)
				print 'Please install first from easy_install, pip, or the instructions below:'
				print MYSQL_PYTHON_INSTRUCTIONS
				return

		try:
			import Crypto
		except:
			import platform
			if platform.system() == 'Darwin':
				print red('You do not have pycrypto installed.', True)
				print 'Please install first from easy_install, pip, or the instructions below:'
				print PYCRYPTO_INSTRUCTIONS
				return

		print 'The following packages will be installed:'
		print '\n'.join(packages)
		print 'Continue? y/n:'
		i = None
		while not i: i = raw_input().lower()
		if i[0] != 'y':
			return
		result = local('which pip', True)
		if result.succeeded:
			for package in packages:
				local('sudo pip install %s' % package)
				if package == 'distribute':
					local('sudo pip install --upgrade distribute')
		else:
			for package in packages:
				if package.startswith('git+git'):
					package = package.replace('git+git', 'https', 1)
					package = package.replace('.git#', '/tarball/master#', 1)
				local('sudo easy_install %s' % package)
				if package == 'distribute':
					local('sudo easy_install -U distribute')
		print ''
		print bold('Note: if you have webapps with this project, these need to be setup seperately - potentially requiring nodejs and running npm install.')

X_COMMAND_MAP = {
					'e': e,
					's': s,
					'localsetup': __localsetup,
					'setups3': __setup_buckets,
					'setupnginx': __setup_nginx,
					'setupuwsgi': __setup_uwsgi,
					'generates3ajax': __generate_s3_ajax,
					'dryrun': __sync_dry_run,
					'uname': __uname,
					'ntp': __ntp,
					'exports': __exports
				}

@task
def x(command=None):
	""" Run another internal command meant for development purposes. For a full list run: fab x """
	if not command:
		print 'Available x commands:\n'
		justification = len(max(X_COMMAND_MAP.keys(), key=len)) + 1
		for name in sorted(X_COMMAND_MAP.keys()):
			print '    %s%s' % (name.ljust(justification), X_COMMAND_MAP[name].__doc__)
	else:
		fun = X_COMMAND_MAP.get(command, None)
		if fun:
			fun()
		else:
			print red('\nError: no such command.\n', True)
			x()
