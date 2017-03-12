#!/usr/bin/env python3

# Copyright Louis Paternault 2011-2015
# This program is free software: you can redistribute it and/or modify
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>. 1

"""Generate dummy pdf files"""

import argparse
import logging
import random
import re
import sys
import textwrap

import papersize

from dummypdf import VERSION
from dummypdf import errors
from dummypdf.pdf import generate, get_color
import dummypdf

LOGGER = logging.getLogger(dummypdf.__name__)
LOGGER.addHandler(logging.StreamHandler())

def positive_int(arg):
    """Return a positive argument corresponding to ``arg``."""
    try:
        number = int(arg)
    except ValueError:
        raise argparse.ArgumentTypeError(arg)
    if number < 0:
        raise argparse.ArgumentTypeError(arg)
    return number

def filename(extension=None):
    """Return the filename.

    - If no argument is provided, return the bare file name.
    - If an argument is provided, it is the extension of the file to be
      returned.
    """

    if extension is None:
        return "dummy"
    else:
        return "dummy.{}".format(extension)

def type_papersize(text):
    """Parse 'text' as the argument of --papersize.

    Return a tuple of :class:`decimal.Decimal`.
    """
    try:
        return papersize.parse_papersize(text)
    except papersize.PapersizeException as error:
        raise argparse.ArgumentTypeError(str(error))

def type_papersize_number(text):
    """Parse 'text' as one of the arguments of --list.

    That is, either a papersize (e.g. "a4"), or a papersize and a page count,
    separated by a colon (e.g. "a4:3").
    """
    try:
        if text.count(":") == 0:
            return (
                papersize.parse_papersize(text),
                1,
                )
        elif text.count(":") == 1:
            paper, count = text.split(":")
            return (
                papersize.parse_papersize(paper),
                int(count),
                )
        else:
            raise argparse.ArgumentTypeError(
                "Argument '{}' must be PAPERSIZE or PAPERSIZE:PAGECOUNT.".format(text)
                )
    except papersize.PapersizeException as error:
        raise argparse.ArgumentTypeError("Paper size error: " + str(error))
    except ValueError as error:
        raise argparse.ArgumentTypeError("Invalid page count: '{}'.".format(count))

class ListColors(argparse.Action):
    """Argparse action to list available named colors."""
    #: pylint: disable=too-few-public-methods

    def __init__(self, *args, **kwargs):
        if 'nargs' in kwargs:
            raise ValueError("nargs not allowed")
        kwargs['nargs'] = 0
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        print(" ".join(get_color()))
        sys.exit(0)

def commandline_parser():
    """Return a command line parser."""

    parser = argparse.ArgumentParser(
        prog="dummypdf",
        description="Generate dummy PDF",
        formatter_class=argparse.RawTextHelpFormatter,
        )

    parser.add_argument(
        '--version',
        help='Show version',
        action='version',
        version='%(prog)s ' + VERSION
        )

    parser.add_argument(
        '--file', '-f',
        default=filename('pdf'),
        help=(
            'Destination file. Default is "dummy.pdf".'
            ),
        type=str,
        )

    parser.add_argument(
        '--number', '-n',
        help=textwrap.dedent("""
        Number of pages. Can be 0 to generate a file with no pages.
        Incompatible with option `--list`.
        """),
        type=positive_int,
        )

    parser.add_argument(
        '--orientation', '-o',
        help="Paper orientation. Default depends on the paper size.",
        default=None,
        choices=["portrait", "landscape"],
        )

    parser.add_argument(
        '--start', '-s',
        help="Number of first page.",
        default=1,
        type=int,
        )

    parser.add_argument(
        '--papersize', '-p',
        type=type_papersize,
        help=textwrap.dedent("""
        Paper size, as either a named size (e.g. "A4" or "letter"), or a couple
        of lengths (e.g. "21cmx29.7cm" or "7in 8in"…). Default value is A4.
        Incompatible with option `--list`.
        """),
        )

    parser.add_argument(
        '--list', '-l',
        type=type_papersize_number,
        help=textwrap.dedent("""
        List of paper size and page count (optional), separated by a colon. The
        paper size format is the same as the argument of `--papersize`; the
        page count is a positive integer (possibly zero). For instance, "--list
        a4 a5:2 a6:0 10cmx100mm 10cmx100mm" will produce a file with one a4
        page, two a5 pages, and two 10cmx100mm pages. Incompatible with options
        `--papersize` and `--number`.
        """),
        nargs="+",
        )

    parser.add_argument(
        '--color', '-c',
        default='deterministic',
        help=textwrap.dedent("""
        Color to use. Can be:

        - deterministic (default): a random color is used, but calls to
          dummypdf using the same arguments give the same color (note that
          calls with different version of this program may lead to different
          colors used).
        - random: a random color is used (different on each call).
        - RED,GREEN,BLUE: a RGB color, where RED, GREEN and BLUE are integers
          between 0 and 255.
        - named colors: Run "dummypdf --list-colors" for the list of available color names.
        """),
    )

    parser.add_argument(
        '--list-colors',
        help='List named colors (to be used with option "--color") and exits.',
        action=ListColors,
        )

    return parser

def pageiterator(options):
    """Iterate over pages to be produced.

    - Argument: The namespace of options (as produced by :mod:`argparse`).
    - Return: An iterator of pages, as tuples ``(FORMAT, COUNT)``, where
      ``FORMAT`` is the page format (as a tuple of ``decimal.Decimal``)
      and the number of pages of this format.
    """
    if options.list is None:
        if options.papersize is None:
            options.papersize = papersize.parse_papersize("a4")
        if options.number is None:
            options.number = 1
        pagelist = [(options.papersize, options.number)]
    else:
        if (options.number is not None) or (options.papersize is not None):
            raise errors.DummyPdfError(
                "Options '--number' and '--papersize' are incompatible with option '--list'."
                )
        pagelist = options.list
    for pageformat in pagelist:
        for _ in range(pageformat[1]):
            if pageformat[0] == (0, 0):
                raise errors.ArgumentError("Error: I cannot produce pages with dimension 0x0.")
            yield (
                float(pageformat[0][0]),
                float(pageformat[0][1]),
                )

def process_options(options):
    "Return processed options (might catch errors unnoticed by :mod:`argparse`."
    processed = {}

    processed['first'] = options.start
    processed['orientation'] = options.orientation
    processed['file'] = options.file

    processed['paperformat'] = list(pageiterator(options))

    color_re = re.compile(r'(?P<red>\w+),(?P<green>\w+),(?P<blue>\w+)')
    if options.color.lower() in ['deterministic', 'random']:
        if options.color.lower() == 'deterministic':
            random.seed("-".join(str(item) for item in [
                processed['first'],
                processed['paperformat'],
                ]))
        processed['color'] = [
            random.randint(64, 255),
            random.randint(0, 191),
            random.randint(0, 255),
            ]
        random.shuffle(processed['color'])
    elif color_re.match(options.color):
        processed['color'] = [int(color) for color in color_re.match(options.color).groups()]
        for color in processed['color']:
            if color > 255:
                raise errors.ArgumentError(
                    "Option '--color' must be an integer between 0 and 255."
                    )
    else:
        processed['color'] = get_color(options.color)

    return processed

def main():
    """Main function"""

    try:
        options = process_options(commandline_parser().parse_args(sys.argv[1:]))
        generate(
            name=options["file"],
            first=options["first"],
            color=options["color"],
            paperformat=options["paperformat"],
            )

    except errors.DummyPdfError as error:
        LOGGER.error(error)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)

if __name__ == "__main__":
    main()
