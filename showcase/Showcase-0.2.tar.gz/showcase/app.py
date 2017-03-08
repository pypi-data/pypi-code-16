#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import humanize
import mimetypes
import os

from flask import Flask, Response, render_template, url_for


app = Flask(__name__)
base = os.getenv('SHOWCASE_DIR', os.getcwd())


def _is_probably_text(path):
    guess, _ = mimetypes.guess_type(path)
    if guess is None:
        text_extensions = ['.md', '.rst']
        return os.path.splitext(path)[1] in text_extensions
    elif guess.startswith('text/') or guess == 'application/json':
        return True
    return False


def _process_path(path):
    url = url_for('show', path=os.path.relpath(path, base))
    name = os.path.basename(path)

    if os.path.isfile(path):
        size = humanize.filesize.naturalsize(os.path.getsize(path))
    else:
        size = '-'
    
    timestamp = datetime.datetime.fromtimestamp(os.path.getctime(path))
    date = humanize.time.naturaltime(timestamp)

    return url, name, size, date


@app.route('/')
@app.route('/<path:path>')
def show(path=None):
    full_path = os.path.join(base, path or '')

    if os.path.isfile(full_path):
        content = open(full_path).read()

        if _is_probably_text(full_path):
            return render_template('file.html', fname=path, body=content)
        else:
            download_name = os.path.basename(full_path)
            return Response(
                content,
                mimetype=mimetypes.guess_type(full_path)[0],
                headers={
                    'Content-Disposition': 'attachment; filename="{}"'.format(download_name),
                },
            )

    dirs = []
    files = []

    # If we're not at the root, add a 'parent' dir
    if path is not None:
        url, name, size, date = _process_path(os.path.dirname(full_path))
        dirs.append([url, '..', size, date])

    for fname in os.listdir(full_path):
        if fname.startswith('.'):
            continue

        thing = os.path.join(full_path, fname)
        url, name, size, date = _process_path(thing)

        if os.path.isfile(thing):
            files.append([url, name, size, date])
        elif os.path.isdir(thing):
            dirs.append([url, name, size, date])

    return render_template(
        'dir.html', path=path or '', files=files, dirs=dirs,
    )
