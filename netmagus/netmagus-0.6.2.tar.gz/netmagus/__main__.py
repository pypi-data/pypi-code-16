# coding=utf-8

import argparse
import codecs
import sys

import netmagus.session

if __name__ == '__main__':
    # BASEDIR = os.path.dirname(inspect.getabsfile(inspect.currentframe()))
    if sys.stdout.encoding != 'UTF-8':
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout, 'strict')
    # handle command line arguments
    parser = argparse.ArgumentParser(
        description='NetMagus NetworkOperation Script')
    parser.add_argument('--script',
                        help='name of the user Python file to execute',
                        required=True)
    parser.add_argument('--input-file',
                        help='full path to a valid NetMagus NetworkOperation '
                             'form JSON output file', required=True)
    parser.add_argument('--token',
                        help='hash key sent by NetMagus to indicate the '
                             'instance of this formula '
                             'execution.  Used by formula to generate RPC '
                             'targets and/or file names for '
                             'responses', required=True)
    parser.add_argument('--loglevel',
                        help='integer 0-5 indicating desired logging level',
                        required=True)
    cli_args = parser.parse_args()
    netmagus.session.NetMagusSession(token=cli_args.token,
                                     input_file=cli_args.input_file,
                                     loglevel=cli_args.loglevel,
                                     script=cli_args.script).start()
