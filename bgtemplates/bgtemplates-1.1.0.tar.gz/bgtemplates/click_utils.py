"""
Functions that use click to ask for parameters,
or that have some relation with click
"""

import os
import re
import click
import logging

from bgtemplates.utils import is_executable, which


def click_check_empty_callback(ctx, param, value):
    if value.strip() == '':
        raise click.BadParameter('It cannot be empty')
    return value


NAME_REGEX = re.compile(r'[^\w.-]')
def click_check_project_name(ctx, param, value):
    value = value.strip()
    if value == '':
        raise click.BadParameter('It cannot be empty')
    if len(value.split()) > 1:
        raise click.BadParameter('It cannot contain spaces or tabs')
    match = NAME_REGEX.search(value)
    if match is not None:
        raise click.BadParameter('Limit the name to letters, numbers, ".", "-" or "_"')
    if not value.islower():
        value = value.lower()
        logging.warning('Converting the name to lowercase: {}'.format(value))
    return value


def ask_for_path(name):
    """
    Get the path where to put the project

    Args:
        name (str): project name

    Returns:
        str. Path

    """
    path = None
    while path is None:
        path = click.prompt('Location for your project', type=click.Path(), default=os.path.join(os.getcwd(), name))
        if os.path.exists(path):
            logging.warning('Path already exist. To avoid overriding, provide a non existing path')
            path = None
    return path


def ask_for_cli(name):
    """
    Get the command under which the user wants his/her command line interface

    Args:
        name (str): project name used as default cmd

    Returns:
        str. Command name

    """
    if click.confirm('Would you like to have a command line interface (cli) in your project?', default=True):
        cmd = click.prompt('Under which command would you like to have the cli', default=name)
        return cmd
    return None


def find_conda():
    """
    Set of question to ask the user for the right path to conda

    Returns:
        str. Path to conda executable

    """
    if click.confirm('Do you want to create a conda environment for the project?', default=True):
        conda_path = which('conda')
        if conda_path is not None:
            if click.confirm('We have found conda in {}. Is this the conda you want to use?'.format(conda_path),
                             default=True):
                return conda_path
        while click.confirm('Sorry, we have not been able to find conda. Do you want to provide the path?', default=True):
            value = click.prompt('Path to conda', type=click.Path(exists=True))
            if is_executable(value):
                return value
        return None
    else:
        return None


def ask_for_conda_env_name(name):
    return click.prompt('Give a name to your environment', default=name)


def ask_for_conda_python_version(version):
    return click.prompt('Which Python version will you like to have?', default=version)


def ask_for_git():
    return click.confirm('Would you like to initialize a git repository in the project folder?', default=True)


def ask_for_remote():
    if click.confirm('Would you like to add a remote repo?', default=False):
        url = click.prompt('URL or path to the remote')
        return url
    return None
