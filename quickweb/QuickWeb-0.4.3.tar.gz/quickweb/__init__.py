import imp
import sys
import os
import os.path
from wsgiref.simple_server import make_server
from quickweb.wsgi import application as wsgi_application_module

import __main__ # Used to identify the app startup script location


def wsgi_application():
    """
        Try to guess the application directory, check for application.py on:
        - Current working directory
        - Directory for the startup script
    """
    possible_entries = (os.getcwd(), os.path.realpath(__main__.__file__))
    app_startup_dir = None
    for path in possible_entries:
        path = os.path.realpath(path)
        if os.path.exists(os.path.join(path, 'application.py')):
            app_startup_dir = path
            break

    if app_startup_dir is None:
        sys.stderr.write('Unable to find startup application.py\n')
        sys.exit(2)

    """ Load the WSGI application """
    wsgi_application = wsgi_application_module.setup(
        'appname', app_startup_dir)
    return wsgi_application


def wsgi_server(wsgi_application, port):
    """ create the wsgi server """

    # Let port be overrided by the envirionemtn variable
    os_port = os.getenv('PORT')
    if os_port is not None:
        port = os_port

    is_gunicorn = "gunicorn" in os.environ.get("SERVER_SOFTWARE", "")
    if is_gunicorn:
        return
    httpd = make_server('', port, wsgi_application)
    print("Serving on *:%d..." % port)
    httpd.serve_forever()
