# -*- coding: utf-8 -*-
"""pystoreql: Store data in free MySQL database via php-crud-api.

Usage:
  pystoreql get [<id>]
  pystoreql post <id> <value>
  pystoreql put <id> <value>
  pystoreql delete <id>
"""

#  from .driver import start_browser
from docopt import docopt
import requests


URL = 'http://mereturn.byethost16.com/pca/api.php/'
COOKIES = {'__test': 'd831f6b86960ab065808406a5c3063bf'}


class PhpCrudApi(object):

    def __init__(self, table_name='t1'):
        self.table_name = table_name
        self.url = URL + table_name
        self.s = requests.Session()
        requests.utils.add_dict_to_cookiejar(
            self.s.cookies,
            COOKIES)

    def get(self, args):
        if args['<id>']:
            r = self.s.get(self.url, params={'filter': 'id,eq,%s' % args['<id>']})
        else:
            r = self.s.get(self.url)
        j = r.json()
        j = j[self.table_name]['records'][0][1]
        print j

    def post(self, args):
        r = self.s.post(self.url, data={'id': args['<id>'], 'value': args['<value>']})
        print r.json()

    def put(self, args):
        r = self.s.put(self.url, data={'id': args['<id>'], 'value': args['<value>']})
        print r.json()

    def delete(self, args):
        r = self.s.delete(self.url, data={'id': args['<id>'], 'value': args['<value>']})
        print r.json()


def main():
    #  browser = start_browser('phantomjs')
    arguments = docopt(__doc__, version='pystoreql 0.1')
    cmd = [arg for arg in arguments if arg[0].isalpha() and arguments[arg]][0]
    pca = PhpCrudApi()
    getattr(pca, cmd)(arguments)


if __name__ == '__main__':
    main()
