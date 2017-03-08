'''
Module for configuration of sys.path for local imports relative to the
directory of the current script entry file.
'''

from .entrydir_pypath import get_entrydir, get_path_list, configure_syspath

configure_syspath()
