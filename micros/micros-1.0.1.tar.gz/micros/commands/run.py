"""The run command, Which is used for local testing"""

from __future__ import absolute_import, division, print_function

from .base import Base
import http.server
import socketserver


class Deploy(Base):
    def run(self):
        """Run the website locally with http.server"""
        port = int(self.options['<port>'])
        handler = http.server.SimpleHTTPRequestHandler
        httpd = socketserver.TCPServer(("", port), handler)
        print('Your dev environment is running on http://localhost:{}'.format(port))
        httpd.serve_forever()
