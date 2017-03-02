"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mfuckery` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``fuckery.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``fuckery.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import argparse
import logging
import os

from fuckery.constants import DEFAULT_MEMORY_SIZE
from fuckery.exc import ExitCondition
from fuckery.parser import parse_program
from fuckery.vm import VirtualMachine

log = logging.getLogger(__name__)


def main(options):
    if not options.verbose:  # pragma: no cover
        logging.disable(logging.DEBUG)
    bn = os.path.basename(options.input)
    with open(options.input, 'rb') as f:
        buf = f.read()

    log.info('Parsing {}'.format(os.path.basename(bn)))
    s = buf.decode()
    tree = parse_program(s=s)
    log.info('Executing {}'.format(os.path.basename(bn)))
    vm = VirtualMachine(memory_size=options.memory_size,
                        loop_detection=options.loop_detection)
    try:
        vm.run(tree=tree)
    except ExitCondition as e:
        log.info(e)
    log.info('Done running program.')


def makeargpaser():  # pragma: no cover
    parser = argparse.ArgumentParser(description='Execute a brainfuck program.')
    parser.add_argument('-i', '--input', dest='input', action='store', type=str, required=True,
                        help='.bf file to execute.')
    parser.add_argument('--loop-detection', dest='loop_detection', default=False, action='store_true',
                        help='Enable loop detection (this has a significant performance impact with large memory).')
    parser.add_argument('--memory-size', dest='memory_size', default=DEFAULT_MEMORY_SIZE, type=int, action='store',
                        help='Memory size to use.  If set too low, programs may fail to run.')
    parser.add_argument('-v', '--verbose', dest='verbose', default=False, action='store_true',
                        help='Enable verbose output.')
    return parser


def _main():  # pragma: no cover
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s [%(levelname)s] %(message)s [%(filename)s:%(funcName)s]')
    p = makeargpaser()
    opts = p.parse_args()
    print(opts)
    main(opts)
