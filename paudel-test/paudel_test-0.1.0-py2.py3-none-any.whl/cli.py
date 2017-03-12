# -*- coding: utf-8 -*-


from __future__ import print_function
# import click
#
# @click.command()
def main(args=None):
    """Console script for paudel_test"""
    # click.echo("Replace this message by putting your code into "
    #            "paudel_test.cli.main")
    # click.echo("See click documentation at http://click.pocoo.org/")

def hello():
    """returns a hellow, world!"""
    return('hello, World!!')
def say_hello():
    """print hello, world message"""
    print (hello())
if __name__ == "__main__":
    main()
