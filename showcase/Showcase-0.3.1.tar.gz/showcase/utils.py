#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import humanize
import mimetypes
import os

from flask import url_for


def is_probably_text(path):
    """Use some poor heurstics to see if we think the file is plain text."""
    guess, _ = mimetypes.guess_type(path)
    if guess is None:
        text_extensions = ['.md', '.rst']
        return os.path.splitext(path)[1] in text_extensions
    elif guess.startswith('text/') or guess == 'application/json':
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
