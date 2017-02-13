
import os
import logging
log = logging.getLogger('prospecting.env')

PROJECTNAME = os.getenv('PROJECTNAME', default='prospecting')
PROJECTDIR = os.getenv('PROJECTDIR', default=os.path.join('path', 'to', 'prospecting'))
CODEDIR = os.getenv('CODEDIR', default=os.path.join('path', 'to', 'prospecting', 'prospecting'))
NOTEBOOKDIR = os.getenv('NOTEBOOKDIR', default=os.path.join('path', 'to', 'prospecting', 'notebooks'))
CREDSDIR = os.getenv('CREDSDIR', default=os.path.join('path', 'to', 'prospecting', 'credentials'))
DATADIR = os.getenv('DATADIR', default=os.path.join('path', 'to', 'prospecting', 'data'))
TMPDIR = os.getenv('TMPDIR', default=os.path.join('path', 'to', 'prospecting', 'data', 'tmp'))

#PROJECTNAME = os.environ['PROJECTNAME']
#PROJECTDIR = os.environ['PROJECTDIR']
#CODEDIR = os.environ['CODEDIR']
#NOTEBOOKDIR = os.environ['NOTEBOOKDIR']
#CREDSDIR = os.environ['CREDSDIR']
#DATADIR = os.environ['DATADIR']
#TMPDIR = os.environ['TMPDIR']

LOG_FILENAME = 'prospecting.log'
LOG_FILENAME_DEBUG = 'debug.log'
LOG_FILE = os.path.join(TMPDIR, LOG_FILENAME)
LOG_FILE_DEBUG = os.path.join(TMPDIR, LOG_FILENAME_DEBUG)

CLIENT_SECRET_FILE = 'client_secret.json'
SOURCE_FILE = 'data.csv'
SOURCE_CSV = os.path.join(DATADIR, SOURCE_FILE)

NOAUTH_LOCAL_WEBSERVER = True


def set_env(projectname, projectdir, codedir, notebookdir, credsdir, datadir, tmpdir):
    PROJECTNAME = projectname
    PROJECTDIR = projectdir
    CODEDIR = codedir
    NOTEBOOKDIR = notebookdir
    CREDSDIR = credsdir
    DATADIR = datadir
    TMPDIR = tmpdir
    env_list = [('PROJECTNAME', PROJECTNAME),
                ('PROJECTDIR', PROJECTDIR),
                ('CODEDIR', CODEDIR),
                ('NOTEBOOKDIR', NOTEBOOKDIR),
                ('CREDSDIR', CREDSDIR),
                ('DATADIR', DATADIR),
                ('TMPDIR', TMPDIR)]
    for var in env_list:
        log.info('Set {0} to {1}'.format(var[0], var[1]))
