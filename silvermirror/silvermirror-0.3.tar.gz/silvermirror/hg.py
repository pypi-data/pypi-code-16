#!/usr/bin/env python

"""
stub for the hg backend of silvermirror
"""

# imports
import argparse
import hglib # http://mercurial.selenic.com/wiki/PythonHglib
import os
import sys
from hglib.error import ServerError

_import_error = None
try:
    import lxml.html
except ImportError as _import_error:
    pass


def clone(source, path):
    print ('Cloning {} -> {}'.format(source, path))
    return hglib.clone(source, path)

def update(source, path):
    """
    get changes from host on path
    """

    if not os.path.exists(path):
        return clone(source, path)

    try:
        repo = hglib.open(path)
        print ('Updating {}'.format(path))
        repo.pull(source, update=True, insecure=True)
    except ServerError:
        repo = hglib.clone(source, path)
    return repo


def repositories(url):
    """
    returns the list of repositories under a URL of an hg server
    """
    element = lxml.html.parse(url)
    tds = element.xpath('//tr[position() > 1]/td[1]')
    repos = [i.text_content() for i in tds]
    return repos


def main(args=sys.argv[1:]):
    """CLI"""

    # parse command line
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('host',
                      help="URL of mercurial repository index page")
    parser.add_argument('-d', '--directory', dest='directory',
                        default=os.path.join(os.environ['HOME'], 'hg'),
                        help="base directory to clone/update to [DEFAULT: %(default)s]")
    parser.add_argument('-r', '--repo', dest='repositories', nargs='+',
                        help="repositories")  # TODO: stub
    parser.add_argument('--list', dest='list',
                      action='store_true', default=False,
                      help="list repositories and exit")
    options = parser.parse_args(args)

    if _import_error is not None:
        # TODO: better error handling
        parser.error("Must have hglib and lxml package to use, sorry:\n{}".format(_import_error))

    # kill trailing slash
    options.host = options.host.rstrip('/')

    # get repositories
    repos = repositories(options.host)
    if options.list:
        for repo in repos:
            print repo
        sys.exit(0)

    # clone/update repos to directory
    if not os.path.exists(options.directory):
        os.mkdir(options.directory)
    for repo in repos:
        source = '{}/{}'.format(options.host, repo)
        dest = os.path.join(options.directory, repo)
        update(source, dest)

if __name__ == '__main__':
    main()
