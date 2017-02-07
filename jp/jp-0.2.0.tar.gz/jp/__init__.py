import click
import tabulate
import json
import csv

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter


def format_json(lines):
    click.echo("[")
    first = True
    for line in lines:
        if not first:
            click.echo(",")
        first = False
        click.echo(highlight(json.dumps(line, indent=2), JsonLexer(), TerminalFormatter()).rstrip(), nl=False)
    click.echo("\n]")


def format_jsonl(lines):
    for line in lines:
        click.echo(highlight(json.dumps(line), JsonLexer(), TerminalFormatter()), nl=False)


def format_table(lines):
    data = list(lines)
    txt = tabulate.tabulate(data, headers="keys")
    click.echo(txt)


def format_list(lines):
    first = False
    for line in lines:
        if first:
            click.echo()
        else:
            first = True
        max_len = max(map(len, line.keys()))
        for k,v in line.items():
            row = "{k:<{max_len}} : {v}".format(k=k, v=v, max_len=max_len)
            click.echo(row)


def format_tsv(lines):
    stdout = click.get_text_stream('stdout')
    writer = csv.writer(stdout, delimiter='\t',  quoting=csv.QUOTE_MINIMAL)
    for line in lines:
        writer.writerow(line.values())

@click.command()
@click.argument('input_file', type=click.File('r'), default=lambda : click.get_text_stream('stdin'))
@click.option('--input', type=click.Choice(['json', 'jsonl']), default='jsonl')
@click.option('--output', type=click.Choice(['json', 'jsonl', 'table', 'list', 'tsv']), default="jsonl")
@click.option('--format')
@click.option('--filter') 
def cli(input_file, input, output, format, filter):
    """Json Lines Formatter"""

    def lines():
        if input == "json":
            lines = json.load(input_file)
        else:
            lines = (json.loads(line) for line in input_file)
        for record in lines:
            if  filter is None or eval(filter, globals(), record):
                yield record 

    formatter = {"json": format_json,
                 "jsonl": format_jsonl,
                 "table": format_table,
                 "list": format_list,
                 "tsv": format_tsv}

    if format is not None:
        for record in lines():
            click.echo(format.format(**record))
    else:
        formatter[output](lines())


if __name__ == '__main__':
    cli()

