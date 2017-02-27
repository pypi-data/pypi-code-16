#!/usr/bin/env python
import click
import codecs
import os


@click.command()
@click.argument('in_files', nargs=-1, type=click.Path(exists=True))
@click.argument('encoding_in', nargs=1)
@click.argument('encoding_out', nargs=1)
def command(in_files, encoding_in, encoding_out):
    for fi in in_files:
        with codecs.open(fi, encoding=encoding_in) as f:
            out_file = os.path.basename(fi)
            with codecs.open(out_file, 'wb', encoding=encoding_out) as o:
                o.write(f.read())


if __name__ == '__main__':
    command()
