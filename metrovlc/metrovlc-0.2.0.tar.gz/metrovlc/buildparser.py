# -*- coding: utf-8 -*-

import argparse

from metrovlc import __version__


def build_parser():
    """ Parser args """
    parser = argparse.ArgumentParser()

    parser.add_argument('-b', '--bono', type=str,
                        dest='bono', default=None,
                        help='Bono info')

    parser.add_argument('-d', '--horario', nargs=2, type=str,
                        dest='horario', default=None,
                        metavar=('ORIGEN', 'DESTINO'),
                        help='Horarios para ORIGEN -> DESTINO')

    parser.add_argument('-ss', '--solo-saldo', action='store_true',
                        dest='solosaldo', default=False,
                        help='Solo muestra el saldo disponible')

    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s ' + __version__)

    return parser
