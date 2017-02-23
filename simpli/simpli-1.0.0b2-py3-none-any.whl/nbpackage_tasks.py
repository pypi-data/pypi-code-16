from os import environ
from os.path import join


def make_data_filepath(filename, namespace=None):
    filepath = '../data/{}'.format(filename).replace('\'', '')
    if isinstance(namespace, dict):
        return '\'{}\''.format(filepath)
    else:
        return filepath


def make_result_filepath(filename, namespace=None):
    filepath = '../results/{}'.format(filename).replace('\'', '')
    if isinstance(namespace, dict):
        return '\'{}\''.format(filepath)
    else:
        return filepath


def _get_dir_tools():
    return join(_get_dir_package(), 'tools/')


def _get_dir_data():
    return join(_get_dir_package(), 'data/')


def _get_dir_results():
    return join(_get_dir_package(), 'results/')


def _get_dir_media():
    return join(_get_dir_package(), 'media/')


def _get_dir_package():
    return environ['DIR_PACKAGE']
