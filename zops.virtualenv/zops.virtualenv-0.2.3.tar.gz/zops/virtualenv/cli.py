# -*- coding: utf-8 -*-
import click


click.disable_unicode_literals_warning = True


@click.group('virtualenv')
def main():
    pass


@main.command()
@click.argument('name')
@click.option('requirements', '-r', multiple=True)
@click.option('editables', '-e', multiple=True)
@click.option('packages', '-i', multiple=True)
@click.option('--python', default='python2')
@click.option('--force', is_flag=True)
def create(name, requirements, editables, packages, python, force):
    """
    Create a virtualenv, caching when possible.
    """
    from zerotk.zops import Console

    venv = _create_venv(name, python)
    if force:
        venv.force_create()
    else:
        venv.open_or_create()
    venv.install('virtualenvwrapper')

    for i_requirement in requirements:
        Console.item('REQUIREMENT: {}'.format(i_requirement))
        Console.output(venv.requirement(i_requirement, force=True, upgrade=True))

    for i_editable in editables:
        Console.item('EDITABLE: {}'.format(i_editable))
        Console.output(venv.editable(i_editable, force=True, upgrade=True))

    for i_package in packages:
        Console.item('PACKAGE: {}'.format(i_package))
        Console.output(venv.install(i_package, force=True, upgrade=True))


def _create_venv(name, python):
    from virtualenvapi.manage import VirtualEnvironment
    import os

    venv_path = os.path.expandvars('${WORKON_HOME}/' + name)
    result = VirtualEnvironment(venv_path, python=python)
    return result
