# -*- coding: utf-8 -*-

import click

from harvest_invoice.invoice import generate


@click.command()
@click.option("--template", help="Template file to be used to generate the invoice.")
def main(template: str):
    generate()


if __name__ == "__main__":
    main()
