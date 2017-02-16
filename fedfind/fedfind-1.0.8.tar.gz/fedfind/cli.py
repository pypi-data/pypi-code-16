#!/usr/bin/python2

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

import argparse
import sys

import fedfind.helpers
import fedfind.release

class Cli(object):
    """Bits for the fedfind CLI tool."""
    def __init__(self):
        self.args = self.parse_args()

    def images(self):
        """images sub-command method. Gets an appropriate Release
        instance and runs an appropriate query, based on the provided
        args.
        """
        try:
            rel = fedfind.release.get_release(
                release=self.args.release, milestone=self.args.milestone,
                compose=self.args.compose)
            print("Finding images for: Fedora {0}").format(rel.version)
        except ValueError as err:
            sys.exit("Invalid arguments. {0}".format(err[0]))
        queries = list()
        if self.args.arch:
            if 'i386' in self.args.arch and not 'i686' in self.args.arch:
                self.args.arch.append('i686')
            elif 'i686' in self.args.arch and not 'i386' in self.args.arch:
                self.args.arch.append('i386')
            queries.append(fedfind.release.Query('arch', self.args.arch))
        if self.args.type:
            queries.append(fedfind.release.Query('imagetype', self.args.type))
        if self.args.payload:
            queries.append(fedfind.release.Query('payload', self.args.payload))
        if self.args.search:
            queries.append(
                fedfind.release.Query('url', self.args.search, exact=False))
        imgs = rel.find_images(queries)
        for img in imgs:
            if self.args.debug:
                print(repr(img))
                print(img.version)
                print(img.payload)
            else:
                print(img)

    def parse_args(self):
        """Parse arguments with argparse."""
        parser = argparse.ArgumentParser(description=(
            "Tool for finding Fedora stuff. Currently finds images, using the "
            "images sub-command. See the image help for more details."))
        subparsers = parser.add_subparsers()
        parser_images = subparsers.add_parser(
            'images', description="Find Fedora images. You must identify a "
            "release, using at least --release or --compose. If you specify "
            "only --release, it must be a Fedora release number, and fedfind "
            "will find images for that stable release. If you specify only "
            "--compose, it must be a date in YYYYMMDD format, and fedfind will"
            " find Rawhide nightly images for that date. If you specify "
            "--release NN --compose YYYYMMDD, fedfind will find Branched "
            "nightly images - you have to provide the release to search "
            "Branched. If you specify --release and --milestone, fedfind will "
            "find images for a pre-release - e.g. --release 22 --milestone "
            "Alpha. If you specify --release, --milestone and --compose, "
            "fedfind will find images for a TC/RC compose - e.g. --release 22 "
            "--milestone Alpha --compose TC1. The other parameters can be "
            "used to filter the results in various ways. For all of the query "
            "parameters, you can specify a single value or several separated "
            "by commas. If you specify several values, fedfind will find "
            "images that match *any* value. If you pass multiple query "
            "parameters, fedfind will only find images that pass the check "
            "for all of the parameters. Matching is exact (but not case-"
            "sensitive) for all parameters except --search, which will match "
            "any image where at least one of the search terms occurs somewhere"
            " in the image URL.")
        parser_images.add_argument(
            '-r', '--release', help="The Fedora release to search", type=int,
            required=False, choices=range(1, 100), metavar="1-99")
        parser_images.add_argument(
            '-m', '--milestone', help="A milestone to search (e.g. Alpha or "
            "Beta)", choices=['Alpha', 'Beta', 'Final'], required=False)
        parser_images.add_argument(
            '-c', '-d', '--compose', '--date', help="A compose or date to "
            "search (e.g. TC1, RC3, or 20150213)", required=False,
            metavar="{T,R}C1-19, 20150213")
        parser_images.add_argument(
            '-a', '--arch', help="Architecture(s) to search for",
            required=False, type=fedfind.helpers.comma_list,
            metavar="armhfp,x86_64...")
        parser_images.add_argument(
            '-t', '--type', help="Image type(s) to search for", required=False,
            metavar="boot,netinst,live...", type=fedfind.helpers.comma_list)
        parser_images.add_argument(
            '-p', '--payload', help="Image payload to search for",
            metavar="workstation,lxde...", required=False,
            type=fedfind.helpers.comma_list)
        parser_images.add_argument(
            '-s', '--search', help="String(s) to search for anywhere in image "
            "URL", required=False, type=fedfind.helpers.comma_list,
            metavar="TERM1,TERM2")
        parser_images.add_argument(
            '--debug', help="Print detailed debugging output",
            required=False, action='store_true')
        parser_images.set_defaults(func=self.images)
        return parser.parse_args()

    def run(self):
        """Read in arguments and run sub-command function."""
        self.args.func()

def main():
    """Main loop."""
    try:
        cli = Cli()
        cli.run()
    except KeyboardInterrupt:
        print("Interrupted, exiting...")
        sys.exit(1)

if __name__ == '__main__':
    main()
