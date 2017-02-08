"""
Module containing git related functions
"""
import os
import shutil

import git
import logging

from bgtemplates.click_utils import ask_for_git, ask_for_remote
from bgtemplates.tips import Tip


def init_repo(folder):
    """
    Initialize a git repository

    Args:
        folder (str): path to the folder where to initialize the repo

    Returns:
        :class:`~git.Repo`.

    """
    logging.info('Initializing git repository: $ git init')
    return git.Repo.init(folder)


def add_gitignore(folder):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    shutil.copyfile(os.path.join(current_dir, 'gitignore.template'), os.path.join(folder, '.gitignore'))


def create_repo(path):
    """
    Initializes a repo and optionally add a remote repository

    Args:
        path (str): path to the folder where to initialize the repo

    """
    if ask_for_git():
        repo = init_repo(path)
        add_gitignore(path)
        remote = ask_for_remote()
        if remote is not None:
            logging.info('Adding remote repository: $ git remote add origin {}'.format(remote))
            repo.create_remote('origin', remote)
            logging.info('Remember to make your first push indicating the remote and the branch: $ git push origin master')
            Tip('Git 1st push', cmd='git push origin master')
