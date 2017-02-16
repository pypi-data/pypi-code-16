#!/bin/python2

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
#
# fedfind finds Fedoras. This is the CLI module.

import argparse
import sys

import fedfind.helpers
import fedfind.release

class Cli(object):
    def __init__(self):
        # 'Valid' TC/RC names
        self.composes=set('{}{}'.format(a, b) for a in ('TC', 'RC')
                          for b in range(1, 21))

    def images(self, args):
        try:
            rel = fedfind.release.get_release(
                    release=args.release, date=args.date,
                    milestone=args.milestone, compose=args.compose)
        except TypeError as e:
            sys.exit("Invalid arguments. You must pass --date or --release, and "
                     "you cannot pass --compose without --milestone.")
        queries = list()
        if args.arch:
            if 'i386' in args.arch and not 'i686' in args.arch:
                args.arch.append('i686')
            elif 'i686' in args.arch and not 'i386' in args.arch:
                args.arch.append('i386')
            queries.append(fedfind.release.Query('arch', args.arch))
        if args.type:
            queries.append(fedfind.release.Query('imagetype', args.type))
        if args.payload:
            queries.append(fedfind.release.Query('payload', args.payload))
        if args.search:
            queries.append(fedfind.release.Query('url', args.search,
                           exact=False))
        imgs = rel.find_images(queries)
        for img in imgs:
            print(img)

    # Comma-separated list of values, or just one (for query params)
    def comma_list(self, string):
        return string.split(',')

    # Date checker that raises an exception on fail. Grr, argparse.
    def datecheck(self, string):
        date = fedfind.helpers.datecheck(string)
        if date:
            return date
        else:
            err = "{} is not a valid date in YYYYMMDD format.".format(string)
            raise argparse.ArgumentTypeError(err)

    def parse_args(self):
        parser = argparse.ArgumentParser(description=(
                "Tool for finding Fedora stuff. Currently finds images, using "
                "the images sub-command. See the image help for more details."))
        subparsers = parser.add_subparsers()
        parser_images = subparsers.add_parser('images', description=
                "Find Fedora images. You must identify a release, using at "
                "least --release or --date. If you specify only --release, it "
                "must be a Fedora release number, and fedfind will find images "
                "for that stable release. If you specify only --date, it must "
                "be a date in YYYYMMDD format, and fedfind will find Rawhide "
                "nightly images for that date. If you specify --release NN "
                "--date YYYYMMDD, fedfind will find Branched nightly images - "
                "you have to provide the release to search Branched. If you "
                "specify --release and --milestone, fedfind will find images "
                "for a pre-release - e.g. --release 22 --milestone Alpha. If "
                "you specify --release, --milestone and --compose, fedfind "
                "will find images for a TC/RC compose - e.g. --release 22 "
                "--milestone Alpha --compose TC1. The other parameters can be "
                "used to filter the results in various ways. For all of the "
                "query parameters, you can specify a single value or several "
                "separated by commas. If you specify several values, fedfind "
                "will find images that match *any* value. If you pass multiple "
                "query parameters, fedfind will only find images that pass the "
                "check for all of the parameters. Matching is exact (but not "
                "case-sensitive) for all parameters except --search, which "
                "will match any image where at least one of the search terms "
                "occurs somewhere in the image URL.")
        parser_images.add_argument('-r', '--release', help="The Fedora release "
                                   "to search", type=int, required=False,
                                   choices=range(1, 100), metavar="1-99")
        parser_images.add_argument('-d', '--date', help="The date of a nightly "
                                   "compose to search", type=self.datecheck,
                                   required=False, metavar="YYYYMMDD")
        parser_images.add_argument('-m', '--milestone', help="A milestone to "
                                   "search (e.g. Alpha or Beta)",
                                   choices=['Alpha', 'Beta', 'Final'],
                                   required=False)
        parser_images.add_argument('-c', '--compose', help="A compose to search"
                                   " (e.g. TC1 or RC3)", choices=self.composes,
                                   metavar="{T,R}C1-19", required=False)
        parser_images.add_argument('-a', '--arch', help="Architecture(s) to "
                                   "search for", required=False,
                                   type=self.comma_list,
                                   metavar="armhfp,x86_64...")
        parser_images.add_argument('-t', '--type', help="Image type(s) to "
                                   "search for", metavar="boot,netinst,live...",
                                   required=False, type=self.comma_list)
        parser_images.add_argument('-p', '--payload', help="Image payload to "
                                   "search for", metavar="workstation,lxde...",
                                   required=False, type=self.comma_list)
        parser_images.add_argument('-s', '--search', help="String(s) to search "
                                   "for anywhere in image URL", required=False,
                                   type=self.comma_list, metavar="SEARCH,TERMS")
        parser_images.set_defaults(func=self.images)
        return parser.parse_args()

    def run(self):
        args = self.parse_args()
        args.func(args)

def main():
    '''Main loop'''
    try:
        cli = Cli()
        cli.run()
    except KeyboardInterrupt:
        print 'Interrupted, exiting...'
        sys.exit(1)

if __name__ == '__main__':
    main()
