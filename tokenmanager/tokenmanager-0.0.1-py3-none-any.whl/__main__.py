import sys
import argparse
import logging

log = logging.getLogger('tokenmanager')

from . import init_token_file, get_tokens, CREATE_HELP

def get_args():
    parser = argparse.ArgumentParser(
        description='''Simple token manager for token-based REST APIs.''',
    )

    parser.add_argument('-i','--init', action='store_true',
                        help='Initialize, create .tokenmanager.yml file')
    parser.add_argument('keys', nargs='*',
                        help='Token keys to print to stdout')

    args = parser.parse_args()

    return args

def main():
    args = get_args()

    if args.init:
        created_path = init_token_file()
        if created_path:
            print('Token file created: {}\n{}'.format(created_path,CREATE_HELP))
    else:
        tokens = get_tokens()
        for key in args.keys:
            errmsg = 'There is no token key ({}) being managed.'.format(key)
            parts = key.split('.')
            comp = tokens
            for k in parts[:-1]:
                if k not in comp:
                    log.error(errmsg)
                    sys.exit(-1)
                comp = comp[k]
            if parts[-1] not in comp:
                log.error(errmsg)
                sys.exit(-1)
            print(comp[parts[-1]])

main()
