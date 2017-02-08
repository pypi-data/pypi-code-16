"""
Module with function related to conda environments
"""
import os
import re
import logging

from bgtemplates.click_utils import ask_for_conda_env_name, ask_for_conda_python_version
from bgtemplates.tips import Tip
from bgtemplates.utils import launch_cmd

CONDA_CMD = '{conda} create -n {name} python={version} {packages} --yes'

CONDA_EXPORT = '{conda} env export -n {name}'

CONDA_FILE_CMD = '{conda} env create -n {name} -f {file} --json'

DEFAULT_PYTHON_VERSION = '3.5' #'.'.join(map(str, [sys.version_info.major, sys.version_info.minor]))

PACKAGE_REGEX = re.compile(r'(?P<package>[a-zA-Z].*?)={1,2}(?P<version>[0-9a-z.]+)(?:=.*?)?')
ENV_PATH_REGEX = re.compile(r'prefix:\s+(?P<path>.*)')


def create_env(conda_path, name, packages=[]):
    """
    Creates a conda environment

    Args:
        conda_path (str): path to conda executable
        name (str): default name for the environment
        packages (list): packages to be installed with conda

    Returns:
        tuple. Environment name, environment path, and packages with versions

    Raises:
        CalledProcessError.

    """

    env_name = ask_for_conda_env_name(name)

    python_version = ask_for_conda_python_version(DEFAULT_PYTHON_VERSION)

    cmd = CONDA_CMD.format(conda=conda_path, name=env_name, version=python_version, packages=' '.join(packages))

    logging.info('Creating conda environment (this may take a while): $ conda create -n {name} python={version} {packages}'.format(name=env_name, version=python_version, packages=' '.join(packages)))

    return_code = os.system(cmd)

    if return_code != 0:
        logging.warning('Error creating the conda environment')
    else:
        logging.debug('Trying to find packages versions')
        cmd = CONDA_EXPORT.format(conda=conda_path, name=env_name)
        try:
            cp = launch_cmd(cmd)
        except Exception as e:
            logging.error('Error trying to get the packages from the environment')
        else:
            output = cp.stdout.decode('utf-8')
            packages_with_versions = {}
            logging.debug(output)
            for g in PACKAGE_REGEX.finditer(output):
                package = g.group('package')
                if package in packages:
                    packages_with_versions[package] = g.group('version')
            match = ENV_PATH_REGEX.search(output)
            logging.debug('match {}'.format(match))
            if match is None:
                logging.debug('Path of the conda env not found')
                logging.warning('Cannot find information about the environment')
                return
            env_path = match.group('path')
            logging.debug('Env path {}'.format(env_path))
            Tip('Activate your conda environment', cmd='source activate {}'.format(env_name))
            return env_name, env_path, packages_with_versions
