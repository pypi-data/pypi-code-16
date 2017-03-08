#!/usr/bin/env python
# -*- coding: utf-8 -*-

import chardet
import mimetypes
import os

from flask import Flask, Response, abort, render_template, request, url_for
from showcase.utils import is_probably_text, process_path


app = Flask(__name__)
base = os.getenv('SHOWCASE_DIR', os.getcwd())


@app.route('/')
@app.route('/<path:path>')
def show(path=None):
    full_path = os.path.join(base, path or '')

    if not os.path.exists(full_path):
        abort(404)

    url = ''
    segments = []
    if path:
        for segment in path.split(os.path.sep):
            url = '{}/{}'.format(url, segment)
            segments.append((url_for('show', path=url), segment))

    # For files, we either display the contents as plain text in a template
    # (possibly stupid if the file is large) or we offer a download if it seems
    # to be binary (or the 'download' query parameter is set).
    if os.path.isfile(full_path):
        content = open(full_path).read()

        if is_probably_text(full_path) and not request.args.get('download'):
            try:
                body = content
                content.decode('utf-8')
            except:
                # If we can't decode as utf-8 it's probably some bizarre
                # encoding that we're going to have to try to sniff out.
                # Unfortunately, this is slow for large files, so we only do it
                # if we have to.
                encoding = chardet.detect(content)['encoding']
                body = content.decode(encoding).encode('utf-8')

            return render_template(
                'file.html', base=base, path=segments, body=body, is_dir=False,
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

    contents = []

    # If we're not at the root, add a 'parent' dir
    if path is not None:
        url, name, size, date = process_path(
            os.path.dirname(full_path), base,
        )
        contents.append([url, '..', size, date])

    for fname in os.listdir(full_path):
        thing = os.path.join(full_path, fname)

        if fname.startswith('.') or os.path.islink(thing):
            continue

        contents.append(process_path(thing, base))

    return render_template(
        'dir.html', base=base, path=segments, contents=contents, is_dir=True,
    )
