# -*- coding: utf-8 -*-
from zerotk.zops import call_main, Console

import click


click.disable_unicode_literals_warning = True


@click.group('code-standards')
def main():
    pass


@main.command()
@click.argument('path')
@click.pass_context
def apply(ctx, path):
    Console.title('zops code-standards apply')
    ctx.invoke(isort, path=path)
    ctx.invoke(autoflake, path=path)
    ctx.invoke(autopep8, path=path)


@main.command()
@click.argument('path')
def isort(path):
    import os
    from isort.main import main as isort_main

    Console.title('zops code-standards isort')
    isort_args = [
        #'--verbose',
        '-m3',
        '-l120',
        #'--order-by-type',
        #'--combine-as',
        #'--force-alphabetical-sort-within-sections',
        #'--force-alphabetical-sort',
        #'--force-sort-within-sections',
        #'--lines-between-types=1',
        #'--atomic',
        #'-y',
        path,
    ]
    if os.path.isdir(path):
        isort_args.insert(0, '--recursive')
    Console.execution('isort', *isort_args)
    call_main(isort_main, *isort_args)


@main.command()
@click.argument('path')
def autoflake(path):
    import os
    from autoflake import main as autoflake_main

    Console.title('zops code-standards autoflake')
    autoflake_args = [
        '-i',
        '--remove-all-unused-imports',
        path
    ]
    if os.path.isdir(path):
        autoflake_args.insert(0, '--recursive')
    Console.execution('autoflake', *autoflake_args)
    call_main(autoflake_main, *autoflake_args)


@main.command()
@click.argument('path')
def autopep8(path):
    import os
    from autopep8 import main as autopep8_main

    Console.title('zops code-standards autopep8')
    autopep8_args = [
        '-a',
        '-i',
        '--max-line-length=120',
        path
    ]
    if os.path.isdir(path):
        autopep8_args.insert(0, '--recursive')
    Console.execution('autopep8', *autopep8_args)
    call_main(autopep8_main, *autopep8_args)
