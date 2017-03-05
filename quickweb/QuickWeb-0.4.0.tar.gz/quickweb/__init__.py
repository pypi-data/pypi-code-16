import imp
import os
import os.path
from wsgiref.simple_server import make_server
from quickweb.wsgi import application as wsgi_application_module

import __main__ # Used to identify the app startup script location


def wsgi_application():
    app_startup_dir = os.path.dirname((os.path.realpath(__main__.__file__)))
    """ Load the WSGI application """
    wsgi_application = wsgi_application_module.setup(
        'appname', app_startup_dir)
    return wsgi_application


def wsgi_server(wsgi_application, port):
    """ create the wsgi server """
    httpd = make_server('', port, wsgi_application)
    print("Serving on localhost:%d..." % port)
    httpd.serve_forever()
