#!/usr/bin/env python
# -*- coding: utf-8 -*-

import chardet
import datetime
import humanize
import mimetypes
import os

from flask import url_for


def is_probably_text(path):
    """Use some poor heurstics to see if we think the file is plain text."""
    guess, _ = mimetypes.guess_type(path)
    if guess and guess.startswith('text/') or guess == 'application/json':
        return True

    text_extensions = ['.md', '.rst']
    if os.path.splitext(path)[1] in text_extensions:
        return True

    # chardet should always be the last resort because it's slow on large files
    detected = chardet.detect(open(path).read())
    if detected['confidence'] >= 0.5 and detected['encoding'] is not None:
        return True

    return False


def process_path(path, base):
    """Given a path and a base dir, return some useful information.
    
    Specifically: a URL that takes you to that path in the app, a friendly
    name, the size (if it's a file) and a humanized version of the created
    timestamp.
    
    """
    url = url_for('show', path=os.path.relpath(path, base))
    name = os.path.basename(path)

    size = '-'
    if os.path.isfile(path):
        size = humanize.filesize.naturalsize(os.path.getsize(path))
    else:
        name += '/'

    try:
        timestamp = datetime.datetime.fromtimestamp(os.path.getctime(path))
    except:
        timestamp = '-'

    date = humanize.time.naturaltime(timestamp)

    return url, name, size, date
