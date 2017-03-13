# -*- coding: utf-8 -*-
'''
Created on Mar 10, 2017

@author: hustcc
'''
from __future__ import absolute_import
from hust import utils
import click
import sys


@click.command()
@click.option('-t', '--type', default='girl',
              type=click.Choice(['girl', 'buddha', 'horse', 'ding']),
              help='The type of funny code comment.')
@click.option('-l', '--lang', default='python',
              type=click.Choice(['python',
                                 'javascript',
                                 'java',
                                 'html',
                                 'css']),
              help='The language of code.')
def ascii_entry(type, lang):
    s = utils.ascii_string(type, lang)
    if s:
        click.echo(utils.ascii_string(type, lang))
    sys.exit(s and 0 or 1)


def run():
    ascii_entry()


if __name__ == '__main__':
    run()
