#---------------------------------------------------------
# Superset specifix config
#---------------------------------------------------------
ROW_LIMIT = 5000
WEBSERVER_THREADS = 8

SUPERSET_WEBSERVER_PORT = 8088
#---------------------------------------------------------

#---------------------------------------------------------
# Flask App Builder configuration
#---------------------------------------------------------
# Your App secret key
SECRET_KEY = '\2\1thisismyscretkey\1\2\e\y\y\h'

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = 'mysql://root@localhost/superset'
#SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://localhost/superset_test'
#SQLALCHEMY_DATABASE_URI = ''

# Flask-WTF flag for CSRF
CSRF_ENABLED = True

# Whether to run the web server in debug mode or not
CACHE_DEFAULT_TIMEOUT = 600
CACHE_CONFIG = {'CACHE_TYPE': 'filesystem', 'CACHE_DIR': '/tmp/superset_cache'}

LANGUAGES = {
    'en': {'flag': 'us', 'name': 'English'},
    'fr': {'flag': 'fr', 'name': 'French'},
    'zh': {'flag': 'cn', 'name': 'Chinese'},
}

MAPBOX_API_KEY = "pk.eyJ1IjoibWlzdGVyY3J1bmNoIiwiYSI6ImNpbjFkMHZscTBhdmh1cmtrdDY1bDV2d2UifQ.vBoVbkMILg2K5GmsmUNxvw"

class CeleryConfig(object):
  BROKER_URL = 'sqla+mysql://root@localhost/superset'
  CELERY_IMPORTS = ('superset.sql_lab', )
  CELERY_RESULT_BACKEND = 'db+mysql://root@localhost/superset'
  CELERY_ANNOTATIONS = {'tasks.add': {'rate_limit': '10/s'}}
CELERY_CONFIG = CeleryConfig
HTTP_HEADERS = {
    'super': 'header!'
}

from werkzeug.contrib.cache import SimpleCache, FileSystemCache
#RESULTS_BACKEND = SimpleCache(threshold=500, default_timeout=300)
RESULTS_BACKEND = FileSystemCache('/tmp/rb', threshold=500, default_timeout=3000)
SQLLAB_DEFAULT_DBID = 1

from flask import Blueprint
simple_page = Blueprint('simple_page', __name__,
                                template_folder='templates')
@simple_page.route('/', defaults={'page': 'index'})
@simple_page.route('/<page>')
def show(page):
    return "PRINT"

BLUEPRINTS = [simple_page]
