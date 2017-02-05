# -*- coding: utf-8 -*-
from __future__ import absolute_import
import click

from .generators import gen_reference_docs


@click.command()
@click.argument('src_dir', metavar='<src_dir>')
@click.argument('dst_dir', metavar='<dst_dir>')
def gendocs(src_dir, dst_dir):
    """ Generate reference documentation for all packages found in src_dir. """
    gen_reference_docs(src_dir, dst_dir)