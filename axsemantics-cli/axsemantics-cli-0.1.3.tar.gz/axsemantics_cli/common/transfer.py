import click
from contextlib import closing
import os
import requests


def auth_header(data):
    return {'Authorization': 'Token {}'.format(data.auth_token)}


def download_with_progressbar(data, url, filename=None, label=None):
    with closing(requests.get(url, stream=True)) as rq:
        if filename is None:
            filename = url.rsplit('/', 1)[-1]
        if label is None:
            label = filename
        chunksize = 1024
        totalsize = int(rq.headers.get('Content-Length', '0').strip())
        kwargs = {
            'show_eta': True,
            'show_percent': True,
            'show_pos': True,
        }
        if label:
            kwargs['label'] = label
        if totalsize > 0:
            kwargs['length'] = int(totalsize / chunksize)

        with click.progressbar(rq.iter_content(chunksize), **kwargs) as bar:
            with open(filename, 'wb') as f:
                for buf in bar:
                    if buf:
                        f.write(buf)


def file_chunker(filename, chunksize):
    with open(filename, 'rb') as f:
        while True:
            buf = f.read(chunksize)
            if buf:
                yield buf
            else:
                break


def upload_with_progressbar(data, url, filename):
    chunksize = 1024

    totalsize = os.path.getsize(filename)
    kwargs = {
        'show_eta': True,
        'show_percent': True,
        'show_pos': True,
        'length': int(totalsize / chunksize),
        'label': 'Uploading {}'.format(os.path.basename(filename)),
    }
    with click.progressbar(file_chunker(filename, chunksize), **kwargs) as bar:
        for buf in bar:
            pass
        # requests.post(url, data=bar, stream=True)
