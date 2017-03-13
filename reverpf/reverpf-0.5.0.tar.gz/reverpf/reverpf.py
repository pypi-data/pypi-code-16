# -*- coding: utf-8 -*-

__author__ = "Pedro Nicolás"
__copyright__ = "Copyright 2017"
__license__ = "MIT"
__version__ = "0.5.0"
__email__ = "png1981@gmail.com"

import sys
import argparse


def build_parser():
    """ Parser args """
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-f', '--format', type=str, required=True,
                        dest='fmt', default=None, metavar='FORMAT',
                        help='Format from printf')
    
    parser.add_argument('-i', '--input-file', type=str,
                        dest='file', default=None, metavar='FILE',
                        help='File input')
    
    parser.add_argument('-s', '--separator', type=str,
                        dest='sep', default=None, metavar='SEPARATOR',
                        help='Separator string')

    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s ' + __version__)

    return parser


def _get_sep_positions(s, sep):
    pos = [i for i in range(len(s)) if s.startswith(sep, i)]

    new_pos = []
    correct = 0

    for i in pos:
        new_pos.append(i - correct)
        correct += len(sep)

    return new_pos


def _cut_by_positions(s, positions, sep='|'):
    n = []
    i = 0
    for j in positions:
        n.append(s[i:j])
        i = j

    n.append(s[i:])

    return sep.join(n) + sep


def rever_printf(fmt, line, sep='|'):

    fmt_sep = fmt.replace('%', '|%')
    count = fmt.count('%')

    # obtenemos la línea tal como sería pero con 0's
    s_zero = fmt_sep % tuple([1] * count)

    positions = _get_sep_positions(s_zero, '|')

    return _cut_by_positions(line, positions, sep)


def rever(input_file, fmt, sep):
    if not input_file:
        finput = sys.stdin
    else:
        finput = open(input_file)

    if not sep:
        sep = ';'

    with finput as f:
        for line in f:
            # print(line)
            line = line.strip('\n')
            rline = rever_printf(fmt, line, sep)
            print(rline)


def main():

    parser = build_parser()
    options = parser.parse_args()

    rever(options.file, options.fmt, options.sep)


if __name__ == '__main__':
    main()
