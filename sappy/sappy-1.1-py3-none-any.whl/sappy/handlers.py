"""Request handlers."""

from http.server import SimpleHTTPRequestHandler
from urllib.parse import urlparse
from pathlib import Path


class SinglePageApplicationHandler(SimpleHTTPRequestHandler):
    """Handler to pass all requests to the index."""

    def do_GET(self):
        """Override GETs for unknown paths."""
        params = urlparse(self.path)
        path = Path(params.path.strip('/'))
        htmlpath = Path(str(path) + '.html')

        if path.exists():
            super().do_GET()

        elif htmlpath.exists():
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            with htmlpath.open('rb') as rfile:
                self.copyfile(rfile, self.wfile)

        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            with Path("index.html").open('rb') as rfile:
                self.copyfile(rfile, self.wfile)
