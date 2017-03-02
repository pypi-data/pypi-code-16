"""Integrate a CSV/TSV file into a distant AskOmics"""

import os
from os.path import basename
import argparse

from libaskocli import askomics_auth
from libaskocli import askomics_url
from libaskocli import RequestApi

class Integrate(object):
    """Integrate a CSV/TSV file into a distant AskOmics"""

    def run(self, args):
        """Integrate a file into a distant askomics

        :param args: script's arguments
        :type args: Namespace
        """

        parser = argparse.ArgumentParser(prog='askocli ' + self.__class__.__name__, description='Integrate data to a distant AskOmics')
        askomics_auth(parser)
        askomics_url(parser)
        parser.add_argument('file', nargs='?', type=str, action="store", help="file to integrate")
        parser.add_argument('--file-type', help='The file type')

        parser.add_argument('-e', '--entities', nargs='*', help='List of entities to integrate')
        parser.add_argument('-t', '--taxon', help='Taxon')

        args = parser.parse_args(args)

        if args.port:
            url = args.askomics + ':' + args.port
        else:
            url = args.askomics

        api = RequestApi(url, args.username, args.apikey, args.file_type)

        api.set_cookie()

        api.set_filepath(args.file)

        api.upload_file()

        ext = os.path.splitext(basename(args.file))[1].lower()

        if ext in ('.gff', '.gff2', '.gff3') or args.file_type == 'gff':
            api.integrate_gff(args.taxon, args.entities)
        elif ext == '.ttl' or args.file_type == 'ttl':
            api.integrate_ttl()
        else:
            api.guess_col_types()
            api.integrate_data()
