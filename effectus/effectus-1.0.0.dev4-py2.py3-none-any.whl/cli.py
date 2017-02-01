"""
    effectus.cli
    ~~~~~~~~~~~~~~~

    Command line scripts of ``effectus.core`` functions and
    variants for Excel of the same that has ``_xl`` as suffix.

    :copyright: (c) 2017 by Benjamin Weber
    :license: MIT, see LICENSE for more details.
"""

import csv

import click
import xlwings as xw

from effectus.helpers import (get_values, sort_effects,
                              format_summary, make_relations)
from effectus.exceptions import (check_and_unfold_vafreqs,
                                 check_valid_limit,
                                 InvalidLimit, ExcelNotOpen,
                                 ExcelNoValuesSelected)
from effectus.core import (make_summary, attain_effects,
                           attain_causes, separate_causes,
                           separate_effects)
from effectus.pareto import ratio


def check_cli_limit(limit):
    """Raises UsageError if limit is not valid."""
    try:
        return check_valid_limit(limit)
    except InvalidLimit:
        raise click.UsageError('Please provide a limit '
                               'between 0 and 1 (including).')


def skip_blanks(xl_vafreqs):
    """Skip blank entries from Excel selection."""
    return list(filter(lambda x: (x is not None and
                                  x != (None, None)),
                       xl_vafreqs))


def populate_xl_vafreqs(xl_vafreqs):
    """Transforms values from list (of lists) to list of
    tuples (observation, frequency).
    """
    if isinstance(xl_vafreqs[0], float):
        return([(value, 1) for value in xl_vafreqs])
    elif len(xl_vafreqs[0]) == 2:
        return([(value, int(freq)) for value, freq in xl_vafreqs])


def process_excel_selection(app_no):
    """Gets values and frequencies from Excel and unfold them."""
    # get Excel instance
    if len(xw.apps) == 0:
        raise ExcelNotOpen('Please ensure Excel to be open.')

    app1 = xw.apps[app_no]

    # select stuff in Excel
    xl_vafreqs = app1.selection.value
    try:
        xl_vafreqs = skip_blanks(xl_vafreqs)
        vafreqs = populate_xl_vafreqs(xl_vafreqs)
        values = check_and_unfold_vafreqs(vafreqs)
        return values
    except TypeError:
        raise ExcelNoValuesSelected


# 2016-11-19: can I make them to be put through by click?
def print_summary(summary):
    """Prints a legible summary."""
    if summary:
        click.echo('{}{}'.format('Pareto'.ljust(15), summary['pareto']))
        click.echo('{}{}'.format('Ratio'.ljust(15), summary['ratio']))
        click.echo('{}{}'.format('Causes'.ljust(15), summary['causes']))
        click.echo('{}{}'.format('Effects'.ljust(15), summary['effects']))
        click.echo('{}{:.2f}'.format('Variability'.ljust(15),
                                     summary['variability']))


@click.command()
@click.argument('filename')
@click.option('-d', '--delimiter', default=',',
              help='Column delimiter (default: \',\')')
@click.option('--observations', default=1, type=click.INT,
              help='Column number of observations (default: 1)')
@click.option('--frequencies', default=2, type=click.INT,
              help='Column number of frequencies (default: 2)')
@click.option('-p', '--precision', default=2,
              help='Number of decimals to show (default: 2)')
def cli_make_summary(filename, delimiter, observations,
                     frequencies, precision):
    """Generates Pareto summary for CSV file."""
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        vafreqs = get_values(reader, observations, frequencies)
        effect_values = check_and_unfold_vafreqs(vafreqs)
        relations = make_relations(effect_values)
        summary = make_summary(relations)
        summary.update(ratio=ratio(effect_values))
        summary.update(pareto=summary['ratio'] <= 1)
        (summary['causes'],
         summary['effects']) = format_summary(summary,
                                              precision)
        print_summary(summary)


@click.command()
def cli_make_summary_xl():
    """Generates Pareto summary for Excel selection."""
    effect_values = process_excel_selection(0)
    relations = make_relations(effect_values)
    summary = make_summary(relations)
    summary.update(ratio=ratio(effect_values))
    summary.update(pareto=summary['ratio'] <= 1)
    (summary['causes'],
     summary['effects']) = format_summary(summary,
                                          precision=3)
    print_summary(summary)


@click.command()
@click.argument('filename')
@click.option('-l', '--limit', default=0.8, type=click.FLOAT,
              help='Effects ratio between 0 and 1 to attain')
@click.option('-d', '--delimiter', default=',',
              help='Column delimiter (default: \',\')')
@click.option('-p', '--precision', default=3,
              help='Number of decimals to show (default: 3)')
@click.option('--observations', default=1, type=click.INT,
              help='Column number of observations (default: 1)')
@click.option('--frequencies', default=2, type=click.INT,
              help='Column number of frequencies (default: 2)')
# pylint: disable=too-many-arguments
def cli_attain_effects(filename, limit, delimiter, precision,
                       observations, frequencies):
    """CLI tool applying ``attain_effects`` on CSV file."""
    check_cli_limit(limit)
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        vafreqs = get_values(reader, observations, frequencies)
        effect_values = check_and_unfold_vafreqs(vafreqs)
        relations = make_relations(effect_values)
        required_causes = attain_effects(relations, limit, precision)
        click.echo('{}{}'.format('Causes'.ljust(15), required_causes))


@click.command()
@click.option('-l', '--limit', default=0.8, type=click.FLOAT,
              help='Effects ratio between 0 and 1 to attain')
@click.option('-p', '--precision', default=3,
              help='Number of decimals to show (default: 3)')
def cli_attain_effects_xl(limit, precision):
    """CLI tool applying ``attain_effects`` on Excel selection."""
    check_cli_limit(limit)
    effect_values = process_excel_selection(0)
    relations = make_relations(effect_values)
    required_causes = attain_effects(relations, limit, precision)
    click.echo('{}{}'.format('Causes'.ljust(15), required_causes))


@click.command()
@click.argument('filename')
@click.option('-l', '--limit', default=0.2, type=click.FLOAT,
              help='Causes ratio between 0 and 1 to attain')
@click.option('-d', '--delimiter', default=',',
              help='Column delimiter (default: \',\')')
@click.option('-p', '--precision', default=3,
              help='Number of decimals to show (default: 3)')
@click.option('--observations', default=1, type=click.INT,
              help='Column number of observations (default: 1)')
@click.option('--frequencies', default=2, type=click.INT,
              help='Column number of frequencies (default: 2)')
# pylint: disable=too-many-arguments
def cli_attain_causes(filename, limit, delimiter, precision,
                      observations, frequencies):
    """CLI tool applying ``attain_causes`` on CSV file."""
    check_cli_limit(limit)
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        vafreqs = get_values(reader, observations, frequencies)
        effect_values = check_and_unfold_vafreqs(vafreqs)
        relations = make_relations(effect_values)
        required_effects = attain_causes(relations, limit, precision)
        click.echo('{}{}'.format('Effects'.ljust(15), required_effects))


@click.command()
@click.option('-l', '--limit', default=0.2, type=click.FLOAT,
              help='Causes ratio between 0 and 1 to attain')
@click.option('-p', '--precision', default=3,
              help='Number of decimals to show (default: 3)')
def cli_attain_causes_xl(limit, precision):
    """CLI tool applying ``attain_causes`` on Excel selection."""
    check_cli_limit(limit)
    effect_values = process_excel_selection(0)
    relations = make_relations(effect_values)
    required_effects = attain_causes(relations, limit, precision)
    click.echo('{}{}'.format('Effects'.ljust(15), required_effects))


@click.command()
@click.argument('filename')
@click.option('-l', '--limit', default=0.2, type=click.FLOAT,
              help='Causes ratio between 0 and 1 to attain (default: 0.2)')
@click.option('-d', '--delimiter', default=',',
              help='Column delimiter (default: \',\')')
@click.option('--observations', default=1, type=click.INT,
              help='Column number of observations (default: 1)')
@click.option('--frequencies', default=2, type=click.INT,
              help='Column number of frequencies (default: 2)')
def cli_separate_causes(filename, limit, delimiter,
                        observations, frequencies):
    """CLI tool applying ``separate_causes`` on Excel selection."""
    check_cli_limit(limit)
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        vafreqs = get_values(reader, observations, frequencies)
        effect_values = check_and_unfold_vafreqs(vafreqs)
        sorted_effects = sort_effects(effect_values)
        (separator, equal,
         total_equals) = separate_causes(sorted_effects, limit)
    click.echo('{}{}'.format('Separator'.ljust(15), separator))
    if equal < total_equals:
        click.echo('{}{}'.format('Element'.ljust(15), equal))
        click.echo('{}{}'.format('of'.ljust(15), total_equals))


@click.command()
@click.option('-l', '--limit', default=0.8, type=click.FLOAT,
              help='Effects ratio between 0 and 1 to attain '
              '(default: 0.8)')
def cli_separate_causes_xl(limit):
    """CLI tool applying ``separate_causes`` on Excel selection."""
    check_cli_limit(limit)
    effect_values = process_excel_selection(0)
    sorted_effects = sort_effects(effect_values)
    separator, equal, total_equals = separate_causes(sorted_effects, limit)
    click.echo('{}{}'.format('Separator'.ljust(15), separator))
    if equal < total_equals:
        click.echo('{}{}'.format('Element'.ljust(15), equal))
        click.echo('{}{}'.format('of'.ljust(15), total_equals))


@click.command()
@click.argument('filename')
@click.option('-l', '--limit', default=0.8, type=click.FLOAT,
              help='Effects ratio between 0 and 1 to attain (default: 0.8)')
@click.option('-d', '--delimiter', default=',',
              help='Column delimiter (default: \',\')')
@click.option('--observations', default=1, type=click.INT,
              help='Column number of observations (default: 1)')
@click.option('--frequencies', default=2, type=click.INT,
              help='Column number of frequencies (default: 2)')
def cli_separate_effects(filename, limit, delimiter,
                         observations, frequencies):
    """CLI tool applying ``separate_effects`` on CSV file."""
    check_cli_limit(limit)
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        vafreqs = get_values(reader, observations, frequencies)
        effect_values = check_and_unfold_vafreqs(vafreqs)
        sorted_effects = sort_effects(effect_values)
        separator, equal, total_equals = separate_effects(sorted_effects,
                                                          limit)
        click.echo('{}{}'.format('Separator'.ljust(15), separator))
        if equal < total_equals:
            click.echo('{}{}'.format('Element'.ljust(15), equal))
            click.echo('{}{}'.format('of'.ljust(15), total_equals))


@click.command()
@click.option('-l', '--limit', default=0.8, type=click.FLOAT,
              help='Effects ratio between 0 and 1 to attain (default: 0.8)')
def cli_separate_effects_xl(limit):
    """CLI tool applying ``separate_causes`` on Excel selection."""
    check_cli_limit(limit)
    effect_values = process_excel_selection(0)
    sorted_effects = sort_effects(effect_values)
    separator, equal, total_equals = separate_effects(sorted_effects,
                                                      limit)
    click.echo('{}{}'.format('Separator'.ljust(15), separator))
    if equal < total_equals:
        click.echo('{}{}'.format('Element'.ljust(15), equal))
        click.echo('{}{}'.format('of'.ljust(15), total_equals))
