from __future__ import print_function, unicode_literals
"""
Provides a WSGI interface for serving web requests. Uses Flask
"""

from flask import request, send_file, g
from io import BytesIO
from werkzeug.datastructures import CombinedMultiDict, MultiDict

class http_server:
    """
    Designed to be used in the function decorated by wsgi_interface
    """

    def __init__(self, content_type = 'application/json'):
        self.content_type = content_type
        # create a default response, in case put isn't called
        g.simpletransfers_wsgi_response = ''

    def get(self):
        files = dict(
            [(f.name, f.read()) for f in request.files.values()]
        )
        return CombinedMultiDict([
            request.values,
            MultiDict(g.simpletransfers_wsgi_request),
            MultiDict(files),
            MultiDict({'_raw': request.data}),
        ])

    def put(self, data, name):
        g.simpletransfers_wsgi_response = send_file(
            BytesIO(data),
            self.content_type,
            attachment_filename=name,
        )

def wsgi_interface(path_function):
    """
    Usage:
    @app.route( '/path/to/api' )
    @wsgi_interface
    def path_function( ... )
    """
    def wrapper(*args, **kwargs):
        g.simpletransfers_wsgi_request = kwargs
        path_function(*args)
        return g.simpletransfers_wsgi_response
    return wrapper
