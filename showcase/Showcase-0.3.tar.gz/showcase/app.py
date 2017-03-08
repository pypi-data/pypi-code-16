#!/usr/bin/env python
# -*- coding: utf-8 -*-

import chardet
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

    size = '-'
    if os.path.isfile(path):
        size = humanize.filesize.naturalsize(os.path.getsize(path))

    try:
        timestamp = datetime.datetime.fromtimestamp(os.path.getctime(path))
    except:
        timestamp = '-'

    date = humanize.time.naturaltime(timestamp)

    return url, name, size, date


@app.route('/')
@app.route('/<path:path>')
def show(path=None):
    full_path = os.path.join(base, path or '')

    url = ''
    segments = []
    if path:
        for segment in path.split(os.path.sep):
            url = '{}/{}'.format(url, segment)
            segments.append((url_for('show', path=url), segment))

    if os.path.isfile(full_path):
        content = open(full_path).read()

        if _is_probably_text(full_path):
            try:
                body = content
                content.decode('utf-8')
            except:
                encoding = chardet.detect(content)['encoding']
                body = content.decode(encoding).encode('utf-8')

            return render_template(
                'file.html', path=segments, body=body,
            )
        else:
            disposition = 'attachment; filename="{}"'.format(
                os.path.basename(full_path),
            )
            return Response(
                content,
                mimetype=mimetypes.guess_type(full_path)[0],
                headers={
                    'Content-Disposition': disposition,
                },
            )

    dirs = []
    files = []

    # If we're not at the root, add a 'parent' dir
    if path is not None:
        url, name, size, date = _process_path(os.path.dirname(full_path))
        dirs.append([url, '..', size, date])

    for fname in os.listdir(full_path):
        thing = os.path.join(full_path, fname)

        if fname.startswith('.') or os.path.islink(thing):
            continue

        url, name, size, date = _process_path(thing)

        if os.path.isfile(thing):
            files.append([url, name, size, date])
        elif os.path.isdir(thing):
            dirs.append([url, name, size, date])

    return render_template(
        'dir.html', path=segments, files=files, dirs=dirs,
    )
