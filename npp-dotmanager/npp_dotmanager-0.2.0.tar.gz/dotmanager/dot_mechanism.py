#! /usr/bin/env python

import os
import yaml

from .command_calling import call_command
from .git_funcitons import git_clone


# Major functions, called from the main file
def clone_public_repo(config):
    """Check if public directory exists and clone to it the public repo."""
    clone_dir = config['repositories']['public']['dir']
    ensure_dir(clone_dir)

    # Try to clone public repository, if directory has content, git will abort
    git_clone(config['repositories']['public']['url'], clone_dir)


def make_private_symlinks(backup_folders, repositories, log):
    """Reads the config and makes symlinks of all entries. Uses functions to \
    ensure folder availability."""

    for foldername, folder in backup_folders.items():

        from_dir = check_dir(repositories['private']['dir'] + '/' + foldername
                             + '/')

        if 'target' not in backup_folders[foldername]:
            backup_folders[foldername]['target'] = '~/'

        to_dir = ensure_dir(backup_folders[foldername]['target'])

        for status, st_dir in folder.items():
            if status == 'target':
                continue
            for dotfile in st_dir:
                from_file, to_file = generate_target_filenames(from_dir, to_dir, dotfile, 'private')
                make_symlink(from_file, to_file, log)
                log.info('{0} is symlinked to {1}'.format(dotfile, to_file))


def make_public_copies(backup_folders, repositories, log):
    "Makes hard copies of files designated public in the config file to the \
    public repository."

    for foldername, folder in backup_folders.items():
        from_dir = check_dir(repositories['private']['dir']) + '/' + foldername + '/'

        target_public = check_slashes(repositories['public']['dir'] + '/' + foldername)

        for status, st_dir in folder.items():
            if status == 'target' or status == 'private':
                continue
            for dotfile in st_dir:
                from_file, to_file = generate_target_filenames(from_dir, target_public, dotfile, 'public')
                ensure_dir(to_file)
                make_copy(from_file, to_file, log)
                log.info('{0} is copied to {1}'.format(dotfile, to_file))


# Loading and reading dotmanager

def read_dotfile(path, def_dotpath, log):
    "Decides if there is a custom dotfile or use default."
    if path:
        log.debug(path)
        return load_dotfile(path, def_dotpath, log)

    dot_path = check_slashes(os.path.expanduser('~') + '/' + def_dotpath)
    log.debug(dot_path)
    return load_dotfile(dot_path, def_dotpath, log)


def load_dotfile(path, def_dotpath, log):
    "Tries to load given config file. If it can't, logs the error: no valid \
    path to dotfile specified, or no file in the default directory (~/.dotfile)"
    try:
        with open(path, 'r') as ymlfile:
            return yaml.load(ymlfile)
    except Exception as e:
        log.error("No dotmanager specified, or ~/{0} not present".format(def_dotpath))
        log.debug(e)


def generate_target_filenames(from_dir, to_dir, dotfile, status):
    """Checks if the filename is a string or a list (as when file has two names,\
    one in backup repository, one in the target directory, for example \
    ranger.conf if backup, and rc.conf when in ~/.config/ranger/rc.conf). \
    If string, it concatenates to the `to` and `from` directories the dotfile's \
    name. If 'private' passed in as status (meaning it symlinks to working \
    dir), makes 'from_file' from_dir + the list's first item, 'to_file' to_dir \
    + the list's second item, if 'public' passed, it'll have the original \
    backup name in the public repository."""
    try:
        assert isinstance(dotfile, str)
        from_file = check_slashes(from_dir + '/' + dotfile)
        to_file = check_slashes(to_dir + '/' + dotfile)
        return from_file, to_file

    except AssertionError:
        if status == 'private':
            if len(dotfile) == 2:
                from_file = check_slashes(from_dir + '/' + dotfile[0])
                to_file = ensure_dir(dotfile[1]) + '/' + os.path.basename(dotfile[1])
                return from_file, to_file

        if status == 'public':
            if len(dotfile) == 2:
                from_file = check_slashes(from_dir + '/' + dotfile[0])
                to_file = check_slashes(to_dir + '/' + dotfile[0])
                return from_file, to_file


def check_slashes(filename):
    "Makes sure there are no double slashes in file path."
    for i in range(len(filename)):
        if i+1 < len(filename):
            if filename[i] == '/' and filename[i+1] == '/':
                filename = filename[:i] + filename[i+1:]
                check_slashes(filename)

    return filename


def make_symlink(from_file, to_file, log):
    "Call symlink shell command."
    command = 'ln -sf {0} {1}'.format(from_file, to_file)
    log.debug('Command called: ' + command)
    call_command(command)


def make_copy(from_file, to_file, log):
    "Call cp shell command."
    command = 'cp {0} {1}'.format(from_file, to_file)
    log.debug('Command called: ' + command)
    call_command(command)


def expand_user(path):
    "Expands the ~ to real user path."
    if path[0] == '~':
        path = os.path.expanduser('~') + path[1:]
    return path


def check_dir(path):
    "Raises error if file doesn't exist."
    path = expand_user(path)
    path = os.path.dirname(path)
    if os.path.exists(path):
        return path
    try:
        raise NameError("No such path exists: {0} Check config and try again.".format(path))
    except NameError as err:
        log.exception('No such file: ', path)


def ensure_dir(path):
    "Checks if dir on path exists, else makes it."
    try:
        value = check_dir(path)
        return value
    except NameError:
        path = expand_user(path)
        path = os.path.dirname(path)
        os.makedirs(path)
        return path

