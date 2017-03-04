# -*- coding: utf-8 -*-
"""pystoreql: A command line tool to easily share pastes and files.

Usage:
  pystoreql get <id>
  pystoreql post <id> <value>
  pystoreql pull <id>
  pystoreql push <id> <file_or_dir>
"""

from docopt import docopt
import requests
from .compression import Archive
import os
from requests.exceptions import ConnectionError
from .config import Config
import sys


class PhpCrudApi(object):

    def __init__(self):
        self.conf = Config()
        self.url = self.conf.url + self.conf.table
        self.s = requests.Session()
        requests.utils.add_dict_to_cookiejar(
            self.s.cookies,
            self.conf.cookies)

    def get(self, args):
        if args['<id>']:
            r = self.s.get(self.url, params={'filter': 'id,eq,%s' % args['<id>']})
        else:
            r = self.s.get(self.url)
        j = r.json()
        j = j[self.conf.table]['records'][0][1]
        print j

    def post(self, args):
        if args['<value>'] == '-':
            value = sys.stdin.read()
        else:
            value = args['<value>']

        r = self.s.post(self.url, data={
            'id': args['<id>'],
            'value': value,
            'type': 'str',
        })

        assert r.status_code == 200
        if r.json() is None:
            print "The `id` already exists!"
        else:
            assert r.json() == 0
        #  print r.json()

    def push(self, args):
        arch = Archive(args['<file_or_dir>'])
        arch.compress()
        ext = ''
        for index, data in enumerate(arch.split()):
            if index:
                ext = str(index)
            r = self.s.post(self.url, data={
                'id': args['<id>'] + ext,
                'value': data,
                'checksum': arch.checksum,
                'type': 'file',
            })
            assert r.status_code == 200
            if r.json() is None:
                print "The `id` already exists!"
                break
            else:
                assert r.json() == 0
            print 'Pushed part: %s' % index
        arch.remove()

    def pull(self, args):
        _id = args['<id>']

        arch = Archive(args['<id>'])
        stage_fn = args['<id>'] + '_stage'

        if os.path.isfile(stage_fn):
            with open(stage_fn, 'rb') as f:
                count = int(f.read())
        else:
            count = 0

        while 1:
            if count:
                _id = args['<id>'] + str(count)
            try:
                r = self.s.get(self.url, params={'filter': 'id,eq,%s' % _id})
            except ConnectionError:
                continue

            j = r.json()
            if j[self.conf.table]['records']:
                j = j[self.conf.table]['records'][0][1]
                with open(arch.ar_path, 'ab') as f:
                    f.write(j.decode('base64'))
                count += 1
                print 'Pulled part: %s' % count

                with open(stage_fn, 'wb') as f:
                    f.write(str(count))
            else:
                break

        arch.decompress()
        arch.remove()
        os.remove(stage_fn)

    def put(self, args):
        r = self.s.put(self.url, data={'id': args['<id>'], 'value': args['<value>']})
        print r.json()

    def delete(self, args):
        r = self.s.delete(self.url, data={'id': args['<id>'], 'value': args['<value>']})
        print r.json()


def main():
    arguments = docopt(__doc__, version='pystoreql 0.1')
    cmd = [arg for arg in arguments if arg[0].isalpha() and arguments[arg]][0]
    pca = PhpCrudApi()
    getattr(pca, cmd)(arguments)


if __name__ == '__main__':
    main()
