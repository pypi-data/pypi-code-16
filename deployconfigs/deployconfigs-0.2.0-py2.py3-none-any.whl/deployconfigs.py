"""
    DeployConfigs

    to lower the pip overhead, I include dj-database-url and dj-cache-url inline
"""

import os
import re

try:  # PY3
    import configparser
    import urllib.parse as urlparse

    BOOLEAN_STATES = dict(configparser.RawConfigParser.BOOLEAN_STATES)  # force copy

except ImportError:  # PY2
    import ConfigParser as configparser
    import urlparse

    BOOLEAN_STATES = dict(configparser.RawConfigParser._boolean_states)  # force copy

try:  # no strict dependency on django. in case it exist we use ImproperlyConfigured from it
    from django.core.exceptions import ImproperlyConfigured
except ImportError:
    class ImproperlyConfigured(Exception):
        pass

DATABASE_SCHEMES = {
    'postgres': 'django.db.backends.postgresql_psycopg2',
    'postgresql': 'django.db.backends.postgresql_psycopg2',
    'pgsql': 'django.db.backends.postgresql_psycopg2',
    'postgis': 'django.contrib.gis.db.backends.postgis',
    'mysql': 'django.db.backends.mysql',
    'mysql2': 'django.db.backends.mysql',
    'mysqlgis': 'django.contrib.gis.db.backends.mysql',
    'mysql-connector': 'mysql.connector.django',
    'spatialite': 'django.contrib.gis.db.backends.spatialite',
    'sqlite': 'django.db.backends.sqlite3',
    'oracle': 'django.db.backends.oracle',
    'oraclegis': 'django.contrib.gis.db.backends.oracle',
}

CACHE_SCHEMES = {
    'db': 'django.core.cache.backends.db.DatabaseCache',
    'dummy': 'django.core.cache.backends.dummy.DummyCache',
    'file': 'django.core.cache.backends.filebased.FileBasedCache',
    'locmem': 'django.core.cache.backends.locmem.LocMemCache',
    'uwsgicache': 'uwsgicache.UWSGICache',
    'memcached': 'django.core.cache.backends.memcached.PyLibMCCache',
    'djangopylibmc': 'django_pylibmc.memcached.PyLibMCCache',
    'pymemcached': 'django.core.cache.backends.memcached.MemcachedCache',
    'redis': 'django_redis.cache.RedisCache',
    'hiredis': 'django_redis.cache.RedisCache',
}

EMAIL_SCHEMES = {
    'smtp': 'django.core.mail.backends.smtp.EmailBackend',
    'smtps': 'django.core.mail.backends.smtp.EmailBackend',
    'console': 'django.core.mail.backends.console.EmailBackend',
    'file': 'django.core.mail.backends.filebased.EmailBackend',
    'memory': 'django.core.mail.backends.locmem.EmailBackend',
    'dummy': 'django.core.mail.backends.dummy.EmailBackend'
}

# Register database, cache, email schemes in URLs.
urlparse.uses_netloc.extend(
    DATABASE_SCHEMES.keys() + CACHE_SCHEMES.keys() + EMAIL_SCHEMES.keys())

DEFAULT_ENV = 'DJANGO_CONF'
DEFAULT_SECTION = 'DJANGO'
TEST_SECTION = 'TEST'
DEFAULT_DATABASE_ENV = 'DATABASE_URL'
DEFAULT_CACHE_ENV = 'CACHE_URL'
DEFAULT_EMAIL_ENV = 'EMAIL_URL'


class DeployConfigs(object):
    def __init__(self,
                 env=DEFAULT_ENV, section=DEFAULT_SECTION,
                 required=None, check_environ=True, use_conf_file=True):
        self.env = env
        self.section = section
        self.required = required or []
        self.check_environ = check_environ
        self.use_conf_file = use_conf_file

        self.ready = False

    def _configure(self):
        django_conf = os.environ.get(self.env)
        if django_conf is None and self.use_conf_file:
            raise ImproperlyConfigured('Please set `%s` environment' % self.env)

        self.cf = configparser.ConfigParser()
        if self.use_conf_file:
            self.cf.read(django_conf)
        self.ready = True

    def get(self, option, default=None, section=None, check_environ=None):
        if not self.ready:
            self._configure()

        if check_environ is None:
            check_environ = self.check_environ

        # let environment overwrite what is in\or not in the conf file.
        if check_environ and section is None:
            val = os.environ.get(option, Undefined)
            if val is not Undefined:
                return val
        try:
            if self.use_conf_file:
                return self.cf.get(section or self.section, option)
            else:
                return default

        except configparser.NoOptionError as e:
            if option in self.required:
                raise e
            return default

    def getboolean(self, option, default=False, section=None, check_environ=None):
        if not self.ready:
            self._configure()

        if check_environ is None:
            check_environ = self.check_environ

        if check_environ and section is None:
            val = os.environ.get(option, Undefined)
            if val is not Undefined:
                return as_boolean(val)

        try:
            return self.cf.getboolean(section or self.section, option)
        except configparser.NoOptionError:
            return default

    def database_dict(self, option=DEFAULT_DATABASE_ENV, default=None, section=None):
        url = self.get(option, section=section) or default
        return self.parse_database_url(url)

    def cache_dict(self, option=DEFAULT_CACHE_ENV, default=None, section=None):
        url = self.get(option, section=section) or default
        return self.parse_cache_url(url)

    def email_dict(self, option=DEFAULT_EMAIL_ENV, default=None, section=None):
        url = self.get(option, section=section) or default
        return self.parse_email_url(url)

    def parse_url(self, url, schemes=None, upper=False):
        if url is None:
            raise ValueError('can not parse_url for None!')
        url = urlparse.urlparse(url)

        backend = None
        if schemes:
            try:
                backend = schemes[url.scheme]
            except KeyError:
                raise ImproperlyConfigured('Unknown scheme `%s`' % url.scheme)

        # Split query strings from path.
        path = url.path[1:]  # ??
        path, query = path, url.query
        if '?' in path and not url.query:
            # Handle python 2.6 broken url parsing
            path, query = path.split('?', 1)

        query_dict = dict([((key.upper() if upper else key), ';'.join(val))
                           for key, val in urlparse.parse_qs(query).items()])
        result = self.Result(
            backend=backend,
            scheme=url.scheme,
            netloc=url.netloc,
            username=urlparse.unquote(url.username or ''),
            password=urlparse.unquote(url.password or ''),
            hostname=url.hostname or '',
            port=url.port or '',
            path=path,
            query=query,
            query_dict=query_dict,
        )
        return result

    class Result(object):
        backend = scheme = netloc = username = password = hostname = port = path = query = query_dict = None

        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    def parse_database_url(self, url):
        if url == 'sqlite://:memory:':
            # this is a special case, because if we pass this URL into
            # urlparse, urlparse will choke trying to interpret "memory"
            # as a port number
            return {
                'ENGINE': DATABASE_SCHEMES['sqlite'],
                'NAME': ':memory:'
            }

        # otherwise parse the url as normal
        url = self.parse_url(url, DATABASE_SCHEMES)

        # If we are using sqlite and we have no path, then assume we
        # want an in-memory database (this is the behaviour of sqlalchemy)
        if url.scheme == 'sqlite' and url.path == '':
            url.path = ':memory:'

        # Handle postgres percent-encoded paths.
        if '%2f' in url.hostname.lower():
            url.hostname = url.hostname.replace('%2f', '/').replace('%2F', '/')

        conn_max_age = url.query_dict.pop('conn_max_age', 0)

        config = {
            'ENGINE': url.backend,
            'NAME': urlparse.unquote(url.path),
            'USER': url.username,
            'PASSWORD': url.password,
            'HOST': url.hostname,
            'PORT': url.port,
            'CONN_MAX_AGE': conn_max_age,
        }

        if url.scheme == 'mysql' and 'ssl-ca' in url.query_dict:
            url.query_dict['ssl'] = {'ca': url.query_dict.pop('ssl-ca')}

        # Support for Postgres Schema URLs
        if 'currentSchema' in url.query_dict and config['ENGINE'] == 'django.db.backends.postgresql_psycopg2':
            url.query_dict['options'] = '-c search_path={0}'.format(url.query_dict['currentSchema'])

        # Pass the query string into OPTIONS if any
        if url.query_dict:
            config.setdefault('OPTIONS', {}).update(url.query_dict)

        return config

    def parse_cache_url(self, url):
        url = self.parse_url(url, CACHE_SCHEMES, upper=True)
        config = {
            'BACKEND': url.backend,
        }

        redis_options = {}
        if url.scheme == 'hiredis':
            redis_options['PARSER_CLASS'] = 'redis.connection.HiredisParser'

        # File based
        if not url.netloc:
            if url.scheme in ('memcached', 'pymemcached', 'djangopylibmc'):
                config['LOCATION'] = 'unix:' + url.path

            elif url.scheme in ('redis', 'hiredis'):
                match = re.match(r'.+?(?P<db>\d+)', url.path)
                if match:
                    db = match.group('db')
                    url.path = url.path[:url.path.rfind('/')]
                else:
                    db = '0'
                config['LOCATION'] = 'unix:%s:%s' % (url.path, db)
            else:
                config['LOCATION'] = url.path

        # URL based
        else:
            # Handle multiple hosts
            config['LOCATION'] = ';'.join(url.netloc.split(','))

            if url.scheme in ('redis', 'hiredis'):
                if url.password:
                    redis_options['PASSWORD'] = url.password
                # Specifying the database is optional, use db 0 if not specified.
                db = url.path[1:] or '0'
                config['LOCATION'] = "%s:%s:%s" % (url.hostname, url.port, db)

        if redis_options:
            config['OPTIONS'] = redis_options

        if url.scheme == 'uwsgicache':
            config['LOCATION'] = config.get('LOCATION', 'default')

        # Pop special options from cache_args
        # https://docs.djangoproject.com/en/1.10/topics/cache/#cache-arguments
        options = {}
        for key in ('MAX_ENTRIES', 'CULL_FREQUENCY'):
            try:
                val = url.query_dict.pop(key)
                options[key] = int(val)
            except KeyError:
                pass

        if options:
            config.setdefault('OPTIONS', {}).update(options)

        config.update(url.query_dict)

        return config

    def parse_email_url(self, url):
        url = self.parse_url(url, EMAIL_SCHEMES)
        config = {
            'EMAIL_BACKEND': url.backend,
            'EMAIL_FILE_PATH': url.path,
            'EMAIL_HOST_USER': url.username,
            'EMAIL_HOST_PASSWORD': url.password,
            'EMAIL_HOST': url.hostname,
            'EMAIL_PORT': url.port,
        }

        use_ssl = False
        use_tls = False
        if url.scheme == 'smtps':
            use_tls = True
        if as_boolean(url.query_dict.get('ssl')):
            use_ssl = True
            use_tls = False  # maybe user use smtps://?ssl=True
        elif as_boolean(url.query_dict.get('tls')):
            use_tls = True
        config['EMAIL_USE_SSL'] = use_ssl
        config['EMAIL_USE_TLS'] = use_tls

        return config

    def parse(self, url):
        if url == 'sqlite://:memory:':
            # this is a special case, because if we pass this URL into
            # urlparse, urlparse will choke trying to interpret "memory"
            # as a port number
            return {
                'ENGINE': DATABASE_SCHEMES['sqlite'],
                'NAME': ':memory:'
            }

        # otherwise parse the url as normal
        url2 = self.parse_url(url, DATABASE_SCHEMES)
        if url2.scheme in DATABASE_SCHEMES:
            return self.parse_database_url(url)
        elif url2.scheme in CACHE_SCHEMES:
            return self.parse_cache_url(url)
        elif url2.scheme in EMAIL_SCHEMES:
            return self.parse_email_url(url)
        else:
            raise ValueError('unknown scheme `%s`' % url2.scheme)


class Undefined(object):
    pass


def as_boolean(val):
    return BOOLEAN_STATES.get(str(val).lower()) is True
