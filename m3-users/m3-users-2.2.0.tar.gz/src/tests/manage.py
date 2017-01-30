#!/usr/bin/python
import os,sys
project_path = os.path.dirname(__file__)


sys.path.insert(0, os.path.join(project_path, '../'))
sys.path.insert(0, os.path.join(project_path, '../env'))
sys.path.insert(0, os.path.join(project_path, '../env/m3/vendor'))

from django.core.management import execute_manager

try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)
