#!/usr/bin/env python

# Copyright (C) 2015 Red Hat
#
# This file is part of fedfind.
#
# fedfind is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Adam Williamson <awilliam@redhat.com>

"""CLI module for fedfind."""

from __future__ import unicode_literals
from __future__ import print_function

import argparse
import logging
import sys

import fedfind.helpers
import fedfind.release

logger = logging.getLogger(__name__)

def _release(rel):
    """Validity check for release parameter - must be an integer or
    rawhide.
    """
    if rel.isdigit() or rel.lower() == 'rawhide':
        return rel
    else:
        raise ValueError("Release must be integer or Rawhide.")

def images(args):
    """images sub-command function. Gets an appropriate Release
    instance and runs an appropriate query, based on the provided
    args.
    """
    try:
        rel = fedfind.release.get_release(
            release=args.release, milestone=args.milestone,
            compose=args.compose, respin=args.respin)
        logger.debug("Release instance: %s", rel)
        logger.info(
            "Finding images for: Fedora %s", rel.version)
    except ValueError as err:
        sys.exit("Invalid arguments. {0}".format(err[0]))
    if args.generic_url:
        print(rel.https_url_generic)
        sys.exit()
    imgs = rel.all_images

    # arch
    if args.arch:
        if 'i386' in args.arch and not 'i686' in args.arch:
            args.arch.append('i686')
        elif 'i686' in args.arch and not 'i386' in args.arch:
            args.arch.append('i386')
        imgs = [img for img in imgs if img['arch'].lower() in args.arch]

    # type
    if args.type:
        imgs = [img for img in imgs if img['type'].lower() in args.type]

    # payload
    if args.payload:
        imgs = [img for img in imgs if
                img['subvariant'].lower() in args.payload]

    # search
    if args.search:
        imgs = [img for img in imgs if any(term in img['path'].lower()
                                           for term in args.search)]

    for img in imgs:
        logger.debug("Subvariant: %s Type: %s Arch: %s", img['subvariant'],
                     img['type'], img['arch'])
        print("{0}/{1}".format(rel.location, img['path']))

def parse_args():
    """Parse arguments with argparse."""
    parser = argparse.ArgumentParser(description=(
        "Tool for finding Fedora stuff. Currently finds images, using the "
        "images sub-command. See the image help for more details."))
    parser.add_argument(
        '-l', '--loglevel', help="The level of log messages to show",
        choices=('debug', 'info', 'warning', 'error', 'critical'),
        default='info')
    # This is a workaround for a somewhat infamous argparse bug
    # in Python 3. See:
    # https://stackoverflow.com/questions/23349349/argparse-with-required-subparser
    # http://bugs.python.org/issue16308
    subparsers = parser.add_subparsers(dest='subcommand')
    subparsers.required = True
    parser_images = subparsers.add_parser(
        'images', description="Find Fedora images. --release, --milestone and "
        "--compose are used to identify the release you wish to find images "
        "for: e.g. -r 23 -m Beta -c RC1, -r 23 -m Branched -c 20150905, -r "
        "23 -m Beta, or -r 22. If the values supplied do not entirely define "
        "a release, fedfind will usually try to guess what you mean. The other"
        " parameters can be used to filter the results in various ways. For "
        "all of the query parameters, you can specify a single value or "
        "several separated by commas. If you specify several values, fedfind "
        "will find images that match *any* value. If you pass multiple query "
        "parameters, fedfind will only find images that pass the check "
        "for all of the parameters. Matching is exact (but not case-"
        "sensitive) for all parameters except --search, which will match "
        "any image where at least one of the search terms occurs somewhere"
        " in the image URL.")
    parser_images.add_argument(
        '-r', '--release', help="The Fedora release to search",
        type=_release, required=False, metavar="1-99 or Rawhide")
    parser_images.add_argument(
        '-m', '--milestone', help="A milestone to search (e.g. Alpha or "
        "Beta)", choices=['Alpha', 'Beta', 'Final', 'Postrelease',
                          'Branched', 'Rawhide', 'Production'])
    parser_images.add_argument(
        '-c', '-d', '--compose', '--date', help="A compose or date to "
        "search (e.g. TC1, RC3, or 20150213)", required=False,
        metavar="{T,R}C1-19, 20150213")
    parser_images.add_argument(
        '-i', '--respin', help="The respin of the compose to search "
        "(an integer)", required=False, type=int)
    parser_images.add_argument(
        '-a', '--arch', help="Architecture(s) to search for",
        required=False, type=fedfind.helpers.comma_list,
        metavar="armhfp,x86_64...")
    parser_images.add_argument(
        '-t', '--type', help="Image type(s) to search for", required=False,
        metavar="boot,netinst,live...", type=fedfind.helpers.comma_list)
    parser_images.add_argument(
        '-p', '--payload', help="Image payload (subvariant) to search for",
        metavar="workstation,lxde...", required=False,
        type=fedfind.helpers.comma_list)
    parser_images.add_argument(
        '-s', '--search', help="String(s) to search for anywhere in image "
        "URL", required=False, type=fedfind.helpers.comma_list,
        metavar="TERM1,TERM2")
    parser_images.add_argument(
        '-g', '--generic-url', help="Just display the HTTPS URL for the "
        "'generic' tree for the given release - the preferred source for "
        "PXE boot kernel/initramfs and so on.",
        required=False, action='store_true')
    parser_images.set_defaults(func=images)
    return parser.parse_args()

def run():
    """Read in arguments, set up logging and run sub-command
    function."""
    args = parse_args()
    loglevel = getattr(
        logging, args.loglevel.upper(), logging.INFO)
    logging.basicConfig(level=loglevel)
    args.func(args)

def main():
    """Main loop."""
    try:
        run()
    except KeyboardInterrupt:
        sys.stderr.write("Interrupted, exiting...\n")
        sys.exit(1)

if __name__ == '__main__':
    main()
