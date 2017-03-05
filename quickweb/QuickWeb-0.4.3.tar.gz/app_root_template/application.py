#!/usr/bin/python
from quickweb import wsgi_application, wsgi_server

application = wsgi_application()

# If invoked from a shell, create an HTTP WSGI server
if __name__ == "__main__":
    wsgi_server(application, 8080)
