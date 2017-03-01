#!/usr/bin/env python
"""
Run `stash -h` for help.
"""
import argparse
import base64
import logging
import os
import requests

_log = logging.getLogger(__name__)

__version__ = '1.0.0'

parser = argparse.ArgumentParser(
    description="Stash files on remote server.")
parser.add_argument(
    '-d', '--debug', action="store_true", help="debug logging")
parser.add_argument(
    '-u', '--url', metavar="URL", default=os.environ.get('STASH_URL'),
    help="URL of remote server, default: env STASH_URL")
parser.add_argument(
    '-t', '--token', metavar="TOKEN", default=os.environ.get('STASH_TOKEN'),
    help="authorization token, default: env STASH_TOKEN")
subparsers = parser.add_subparsers(title='command')
subparser = subparsers.add_parser('push')
subparser.set_defaults(command='push')
subparser.add_argument('box', metavar="BOX", help="name of stash box")
subparser.add_argument(
    'file_path', metavar="PATH",
    help="path to file to be stashed, required for stashing")
subparser.add_argument(
    'name', metavar="NAME", nargs='?',
    help="name of the file, default: file path's basename")
subparser = subparsers.add_parser('pull')
subparser.set_defaults(command='pull')
subparser.add_argument('box', metavar="BOX", help="name of stash box")
subparser.add_argument(
    '-c', '--check-count', metavar="CNT",
    help="Validate count of stashed files in the box")
subparser.add_argument(
    '-b', '--base-dir', metavar="DIR",
    help="Base directory to pull stash to, default is current dir.")


class Stasher(object):
    def __init__(self, url, token=None):
        assert url
        self.url = url
        self.token = token

    def headers(self):
        if self.token:
            return {'Authorization': 'Token ' + self.token}
        else:
            return {}

    def push(self, box, path, name=None):
        assert box
        assert path
        if not name:
            name = os.path.basename(path)
        f = open(path, 'rb')
        try:
            r = requests.post(url=self.url + '/push',
                              data={'box': box, 'name': name},
                              headers=self.headers(),
                              files={'file': f})
        except requests.RequestException as e:
            _log.error(str(e))
        else:
            if not r.ok:
                _log.error('%s', r.text)

    def pull(self, box, check_count, base_dir):
        r = requests.get(url=self.url + '/pull',
                         params={'box': box, 'count': check_count},
                         headers=self.headers())
        if r.ok:
            for k, v in r.json().items():
                path = os.path.basename(k)
                if base_dir:
                    path = os.path.join(base_dir, path)
                path = os.path.abspath(path)
                _log.info(path)
                with open(path, 'wb+') as fp:
                    fp.write(base64.b64decode(v.encode()))
        else:
            _log.error('%s', r.text)


def main():
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    stasher = Stasher(url=args.url, token=args.token)
    if args.command == 'push':
        stasher.push(box=args.box, path=args.file_path, name=args.name)
    if args.command == 'pull':
        stasher.pull(box=args.box, check_count=args.check_count,
                     base_dir=args.base_dir)

if __name__ == '__main__':
    main()
