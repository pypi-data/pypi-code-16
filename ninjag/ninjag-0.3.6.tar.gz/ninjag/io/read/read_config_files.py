"""
Read all the user configuration files
and return a combined dictionary
"""
import yaml
from ...tk import fnTK, dictTK, ioTK
from .check_input import check_input
from .default_config import default_config


def read_config_files(files):
    """Read config files

    Args:
        files (str): a list of file names
    Returns:
        a dict
    """
    fn = fnTK.compose([ioTK.read_all, yaml.load])
    return check_input(
        dictTK.merge([default_config()] + list(map(fn, files))))
