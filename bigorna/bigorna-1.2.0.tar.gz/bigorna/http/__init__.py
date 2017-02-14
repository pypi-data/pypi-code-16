import logging

from flask import Flask, url_for, redirect

from .rest import api
from .webview import web


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S')

app = Flask('Bigorna')
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(web, url_prefix='/_')


@app.route('/')
def index():
    return redirect(url_for('webview.index'))


@app.route('/ping')
def heartbeat():
        return '<html><body style="font-family:courier new;">pong!</body></html>'


@app.template_filter('datefmt')
def _jinja2_filter_datetime(date):
    if date:
        fmt = '%d/%m/%y %H:%M:%S'
        return date.strftime(fmt)
