import logging
from subprocess import check_call

import click
from path import Path

from sblu.cli import pass_context
from sblu.util import which

logger = logging.getLogger(__name__)
DEFAULTS = [
    '-T', "FFTW_EXHAUSTIVE",
    '-t', "1",
    '-c', '1.0',
    '--msur_k', '1.0',
    '--maskr', '1.0',
    '-k', '4'
]


@click.command('piper', help="Helpful wrapper for PIPER with sensible defaults.")
@click.option('-R', 'n_rotations', type=click.INT, default=-1)
@click.option('-p', '--atmprm', type=click.Path(exists=True))
@click.option('-f', '--coeffs', type=click.Path(exists=True))
@click.option('-r', '--rotprm', type=click.Path(exists=True))
@click.option('-O', '--output-dir', type=click.Path())
@click.argument('rec', type=click.Path(exists=True))
@click.argument('lig', type=click.Path(exists=True))
@pass_context
def cli(ctx, n_rotations,
        atmprm, coeffs, rotprm, output_dir,
        rec, lig):
    piper_bin = which('piper', required=True)
    logger.info('using piper {}'.format(piper_bin))

    if atmprm is None:
        atmprm = 'atoms.prm'
    if coeffs is None:
        coeffs = 'coeffs.prm'
    if rotprm is None:
        rotprm = 'rots.prm'

    cmd = [piper_bin]
    cmd += DEFAULTS
    if n_rotations is not None:
        cmd += ['-R', str(n_rotations)]
    if output_dir is not None:
        Path(output_dir).mkdir_p()
        cmd += ['-O', output_dir]
    cmd += ['-p', atmprm]
    cmd += ['-f', coeffs]
    cmd += ['-r', rotprm]
    cmd += [rec, lig]

    print(cmd)
    logger.info(' '.join(cmd))
    check_call(cmd)
