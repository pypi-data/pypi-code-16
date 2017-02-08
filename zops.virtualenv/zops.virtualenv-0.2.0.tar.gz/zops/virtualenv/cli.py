# -*- coding: utf-8 -*-
import click


click.disable_unicode_literals_warning = True


@click.group('virtualenv')
def main():
    pass


@main.command()
@click.argument('name')
@click.option('--python', default='python2')  # , options=('python2', 'python3'))
@click.option('requirements', '-r', multiple=True)
@click.option('editables', '-e', multiple=True)
@click.option('packages', '-i', multiple=True)
def create(name, python, requirements, editables, packages):
    """
    Create a virtualenv, caching when possible.
    """
    from zerotk.zops import Console

    venv = _create_venv(name, python)
    venv.force_create()
    venv.install('virtualenvwrapper')

    for i_requirement in requirements:
        Console.item('REQUIREMENT: {}'.format(i_requirement))
        Console.output(venv.install('-r {}'.format(i_requirement), force=True, upgrade=True))

    for i_editable in editables:
        Console.item('EDITABLE: {}'.format(i_editable))
        Console.output(venv.install('-e {}'.format(i_editable), force=True, upgrade=True))

    for i_package in packages:
        Console.item('PACKAGE: {}'.format(i_package))
        Console.output(venv.install(i_package, force=True, upgrade=True))


def _create_venv(name, python):
    from virtualenvapi.manage import VirtualEnvironment
    import os

    class MyVirtualEnvironment(VirtualEnvironment):

        def force_create(self):
            import shutil
            shutil.rmtree(self.name, ignore_errors=True)
            self._create()

        def requirement(self, requirement):
            return self._execute_pip(['install', '-U', '-r', requirement])

    venv_path = os.path.expandvars('${WORKON_HOME}/' + name)
    result = MyVirtualEnvironment(venv_path, python=python)
    return result
