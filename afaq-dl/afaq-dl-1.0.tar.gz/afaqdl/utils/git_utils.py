# -*- coding: utf-8 -*-

# Copyright 2016 juxor <ju@riseup.net>

# This file is part of afaq-dl.
#
# afaq-dl is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# afaq-dl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with afaq-dl.  If not, see <http://www.gnu.org/licenses/>.

import logging
import sys
import io
from os import environ, makedirs, chmod
from os.path import isdir, isfile
from shutil import rmtree
from git import Repo, InvalidGitRepositoryError, GitCmdObjectDB, \
    GitCommandError

from .system import write_metadata_file


logger = logging.getLogger(__name__)

__all__ = ['check_ssh_keys',
     'clone_repo',
     'commit_push',
     'commit_push_if_changes',
     'create_repo',
     'obtain_repo',
     'pull_repo',
     'write_ssh_command',
     'write_ssh_key_server',
     'write_ssh_keys']


def obtain_repo(local_repo_path, data_remote_repo,
                  git_ssh_command_path=None,
                  exit_on_error=True):
    local_repo = None
    logger.debug("OBTAINING REPO")
    if isdir(local_repo_path):
        logger.debug('Directory %s exist.' % local_repo_path)
        try:
            local_repo = Repo(local_repo_path, odbt=GitCmdObjectDB)
            logger.debug('The directiory is a git repository.')
            remote_repo = local_repo.remotes[data_remote_repo.get('name')]
        # dir exist but is not a repo
        except InvalidGitRepositoryError as e:
            logger.debug('The directiory is not a git repository.')
            rmtree(local_repo_path)
            logger.debug('Directiory removed.')
            try:
                local_repo, remote_repo = clone_repo(
                                            local_repo_path,
                                            data_remote_repo,
                                            git_ssh_command_path)
            except GitCommandError as e:
                logger.debug('Can not clone repository %s',
                             data_remote_repo.get('url'))
                if exit_on_error:
                    sys.exit()
                else:
                    local_repo, remote_repo = create_repo(
                                                local_repo_path,
                                                data_remote_repo)
        else:
            pull_repo(remote_repo, data_remote_repo, git_ssh_command_path)
            # FIXME: pull fail?
        return local_repo, remote_repo
    try:
        local_repo, remote_repo = clone_repo(local_repo_path,
                                             data_remote_repo,
                                             git_ssh_command_path)
    except GitCommandError as e:
        logger.debug('Can not clone repo %s.', e)
        if exit_on_error:
            sys.exit()
        else:
            local_repo, remote_repo = create_repo(local_repo_path,
                                                  data_remote_repo)
    return local_repo, remote_repo


def pull_repo(remote_repo,
              data_remote_repo,
              git_ssh_command_path=None):
    logger.info("PULLING")
    logger.info('Remote repository url %s named %s branch %s.' %
                (remote_repo.url, remote_repo.name,
                 data_remote_repo.get('branch')))
    try:
        if git_ssh_command_path:
            logger.debug('Pulling with git_ssh_command_path %s.' %
                         git_ssh_command_path)
            with remote_repo.repo.git.custom_environment(
                    GIT_SSH=git_ssh_command_path):
                remote_repo.pull(data_remote_repo.get('branch'))
        else:
            logger.debug('Pulling without git_ssh_command_path.')
            remote_repo.pull(data_remote_repo.get('branch'))
        logger.debug('Successfully pulled.')
    except GitCommandError as e:
        # FIXME: handle better exception
        logger.debug('Can not pull repository.')
        raise e


def clone_repo(local_repo_path, data_remote_repo,
               git_ssh_command_path=None):
    logger.info("CLONING")
    logger.info('Repository %s, branch %s named %s in %s.'
                % (data_remote_repo.get('url'),
                   data_remote_repo.get('branch'),
                   data_remote_repo.get('name'),
                   local_repo_path))
    try:
        if git_ssh_command_path:
            logger.debug('Cloning with git_ssh_command_path %s.' %
                         git_ssh_command_path)
            local_repo = Repo.clone_from(
                            data_remote_repo.get('url'),
                            local_repo_path,
                            branch=data_remote_repo.get('branch'),
                            env={'GIT_SSH': git_ssh_command_path}
                         )
        else:
            logger.debug('Pulling without git_ssh_command_path.')
            local_repo = Repo.clone_from(
                            data_remote_repo.get('url'),
                            local_repo_path,
                            branch=data_remote_repo.get('branch')
                         )
        logger.debug('Successfully cloned.')
        remote_repo = local_repo.remotes['origin']
        remote_repo.rename(data_remote_repo.get('name'))
        logger.debug('Repository remote origin renamed %s.' %
                     data_remote_repo.get('name'))
        return local_repo, remote_repo
    except GitCommandError as e:
        logger.debug('Could not clone repo.')
        raise e


def create_repo(local_repo_path, data_remote_repo):
    logger.info("CREATING REPO")
    logger.info('Repository %s named %s in %s.' %
                (data_remote_repo.get('url'),
                 data_remote_repo.get('name'),
                 local_repo_path))
    local_repo = Repo.init(local_repo_path)
    logger.debug('Successfully created repository %s.' % local_repo_path)
    remote_repo = local_repo.create_remote(data_remote_repo.get('name'),
                                           data_remote_repo.get('url'))
    logger.debug('Successfully created repository remote %s named %s' %
                 (data_remote_repo.get('url'), data_remote_repo.get('name')))
    return local_repo, remote_repo


def commit_push(local_repo, repo_author, repo_email, git_ssh_command_path,
                data_remote_repo):
    logger.info("COMMITING")
#    r = local_repo.index.add('*')
#    files = '\n'.join([f[3] for f in r])
#    logger.debug('Added files to repo %s', files)
    r = local_repo.git.add(update=True)
    # TODO check for deleted files
    # TODO: check for untracket files
    commit_msg = "Automatic crawling"
    environ["GIT_AUTHOR_NAME"] = repo_author
    environ["GIT_AUTHOR_EMAIL"] = repo_email
    # commit only if something changed
    committed = local_repo.index.commit(commit_msg)
#    try:
#        committed = local_repo.index.commit(commit_msg)
#    except TypeError as e:
#        logger.error('Something happened when commiting %s', e)
    logger.info('Commited data')
#    logger.info(committed.hexsha)
    logger.info('PUSHING')
    remote_repo = local_repo.remotes[data_remote_repo.get('name')]
    logger.info('To repository %s named %s' % (remote_repo.url,
                                               remote_repo.name))
    logger.debug('pushing with git_ssh_command_path %s' %
                 git_ssh_command_path)
    # more debugging for morph.io
    with io.open(git_ssh_command_path) as f:
        logger.debug('ssh command content %s' % f.read())
    with remote_repo.repo.git.custom_environment(GIT_SSH=git_ssh_command_path):
        environ['GIT_SSH'] = git_ssh_command_path
        logger.debug('GIT_SSH %s' % environ.get('GIT_SSH'))
        logger.debug('GIT_SSH_COMMAND %s' % environ.get('GIT_SSH_COMMAND'))
        try:
            remote_repo.push(data_remote_repo.get('branch'))
        except GitCommandError as e:
            # FIXME: handle better exception
            logger.debug('Can not push.')
            raise(e)


def commit_push_if_changes(local_repo, repo_author, repo_email,
                           git_ssh_command_path,
                           data_remote_repo, metadata_path):
    # FIXME: handle changes to be commited
#    if local_repo.index.diff(None) or local_repo.untracked_files:
    if local_repo.is_dirty():
        write_metadata_file(metadata_path, local_repo.working_dir)
        commit_push(local_repo, repo_author, repo_email, git_ssh_command_path,
                    data_remote_repo)
    else:
        logger.debug('nothing changed, not committing/pushing')


def write_ssh_keys(ssh_dir, ssh_priv_key_env, ssh_pub_key_env,
                   ssh_priv_key_path, ssh_pub_key_path):
    ssh_pub_key = environ[ssh_pub_key_env]
    ssh_priv_key = environ[ssh_priv_key_env]
    logger.debug('ssh_dir %s' % ssh_dir)
    if not isdir(ssh_dir):
        makedirs(ssh_dir)
        logger.debug('created dir %s' % ssh_dir)
    if not isfile(ssh_pub_key_path):
        with io.open(ssh_pub_key_path, 'wb') as f:
            f.write(ssh_pub_key)
        logger.debug('wroten %s' % ssh_pub_key_path)
    if not isfile(ssh_priv_key_path):
        with io.open(ssh_priv_key_path, 'wb') as f:
            f.write(ssh_priv_key)
        logger.debug('wroten %s' % ssh_priv_key_path)
        # 0600
        chmod(ssh_priv_key_path, 2 ** 8 + 2 ** 7)


def write_ssh_command(git_ssh_command_path, git_ssh_command):
    if not isfile(git_ssh_command_path):
        with io.open(git_ssh_command_path, 'w') as f:
            f.write(git_ssh_command)
        # 0766
        chmod(git_ssh_command_path, 2 ** 8 + 2 ** 7 + 2 ** 6 +
                                    2 ** 5 + 2 ** 4 +
                                    2 ** 3 + 2 ** 2)
        logger.debug('wroten %s' % git_ssh_command_path)
        logger.debug('with content %s' % git_ssh_command)


def write_ssh_key_server(ssh_pub_key, ssh_pub_key_path):
    if not isfile(ssh_pub_key_path):
        with io.open(ssh_pub_key_path, 'w') as f:
            f.write(ssh_pub_key)
        logger.debug('wroten %s' % ssh_pub_key_path)
        logger.debug('with content %s' % ssh_pub_key)


def check_ssh_keys(local_repo, git_ssh_command_path, ssh_priv_key_path,
                   ssh_pub_key_path, ssh_pub_key_path_server):

    with io.open(ssh_pub_key_path, 'r') as f:
        logger.debug('ssh pub key %s' % f.read())
    with io.open(ssh_priv_key_path, 'r') as f:
        logger.debug('ssh priv key %s' % f.read())
    with io.open(ssh_pub_key_path_server, 'r') as f:
        logger.debug('ssh pub key server %s' % f.read())
    remote_repo = local_repo.remotes[0]
    logger.debug('pushing with git_ssh_command_path %s' %
                 git_ssh_command_path)
    # more debugging for morph.io
    with io.open(git_ssh_command_path) as f:
        logger.debug('ssh command content %s' % f.read())
    logger.debug('MORPH_SSH_PUB_KEY')
    logger.debug(environ.get('MORPH_SSH_PUB_KEY'))
    logger.debug('MORPH_SSH_PRIV_KEY')
    logger.debug(environ.get('MORPH_SSH_PRIV_KEY'))
    with local_repo.git.custom_environment(GIT_SSH=git_ssh_command_path):
        logger.debug('GIT_SSH %s' % environ.get('GIT_SSH'))
        logger.debug('GIT_SSH_COMMAND %s' % environ.get('GIT_SSH_COMMAND'))
    with remote_repo.repo.git.custom_environment(GIT_SSH=git_ssh_command_path):
        logger.debug('GIT_SSH %s' % environ.get('GIT_SSH'))
        logger.debug('GIT_SSH_COMMAND %s' % environ.get('GIT_SSH_COMMAND'))
    environ['GIT_SSH'] = git_ssh_command_path
    logger.debug('GIT_SSH %s' % environ.get('GIT_SSH'))
