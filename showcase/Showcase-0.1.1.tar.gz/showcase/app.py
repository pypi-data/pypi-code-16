#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import humanize
import os

from urlparse import urlparse

from flask import Flask, render_template, url_for
from gunicorn.app.base import BaseApplication


app = Flask(__name__)
base = os.getenv('SHOWCASE_DIR', os.path.abspath(os.path.dirname(__file__)))


def _process_path(path):
    rel = os.path.relpath(path, base)
    if rel == '.':
        rel = '..'

    if os.path.isfile(path):
        size = humanize.filesize.naturalsize(os.path.getsize(path))
    else:
        size = '-'
    
    timestamp = datetime.datetime.fromtimestamp(os.path.getctime(path))
    date = humanize.time.naturaltime(timestamp)

    return rel, size, date


@app.route('/')
@app.route('/<path:path>')
def show(path=None):
    full_path = os.path.join(base, path or '')

    if os.path.isfile(full_path):
        return render_template(
            'file.html', fname=path, body=open(full_path).read()
        )

    dirs = []
    files = []

    if path is not None:
        dirs.append(_process_path(base))

    for fname in os.listdir(full_path):
        if fname.startswith('.'):
            continue

        thing = os.path.join(full_path, fname)
        rel, size, date = _process_path(thing)

        if os.path.isfile(thing):
            files.append([rel, size, date])
        elif os.path.isdir(thing):
            dirs.append([rel, size, date])

    return render_template(
        'dir.html', path=path or '', files=files, dirs=dirs,
    )
