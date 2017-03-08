#!/usr/bin/python
'''
Module for configuration of sys.path for local imports relative to the
directory of the current script entry file.
'''

import os
import sys


def get_entrydir():
    '''
    Returns the directory of the current script entry point.
    '''
    if hasattr(sys, 'argv'):
        return os.path.realpath(os.path.dirname(sys.argv[0]))

    # Fallback for import via usercustomize for an interactive script session
    # and other special cases
    return os.getcwd()


def get_pathfile(base):
    '''
    Returns the path for the path-specification file for the given
    directory 'base'.
    '''
    return os.path.join(base, '.pythonpath')


def get_path_list(base=None):
    '''
    Returns a list of absolute paths derived from the found path-specification
    files, starting the search in the given directory 'base'.
    '''
    if base is None:
        base = get_entrydir()
    while not os.path.isfile(get_pathfile(base)):
        parent = os.path.split(base)[0]
        if parent == base:
            return []
        base = parent

    i = 0
    path_list = []
    to_check = [base]
    while i < len(to_check):
        for line in open(get_pathfile(to_check[i])):
            path = line.strip()
            if not os.path.isabs(path):
                path = os.path.join(to_check[i], path)
            path = os.path.normpath(path)
            if os.path.isdir(path):
                if path != to_check[i] and os.path.isfile(get_pathfile(path)):
                    selection = to_check
                else:
                    selection = path_list
                if path not in selection:
                    selection.append(path)
        i += 1

    return path_list


def configure_syspath(path_list=None):
    '''
    Appends paths to sys.path in accordance to the found path-specification
    files, starting the search in the directory of the current script entry
    point.
    '''
    if path_list is None:
        path_list = get_path_list()
    for path in path_list:
        if path not in sys.path:
            sys.path.append(path)
