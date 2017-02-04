import os
import sys
import subprocess
import logging

logger = logging.getLogger(__name__)

def _check_output(command, cwd):
    stdout = subprocess.check_output(command, cwd=cwd, universal_newlines=True,
                               stderr=subprocess.PIPE)
    return stdout.strip()

def _get_success(command, cwd):
    try:
        subprocess.check_call(command, cwd=cwd, universal_newlines=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

def _is_git_repo(cwd=None):
    return _get_success(['git', 'status'], cwd=cwd)

def repo_name(cwd=None):
    git_top_level = _check_output(['git', 'rev-parse', '--show-toplevel'], cwd=cwd)
    return os.path.basename(git_top_level)

def version_number(cwd=None):
    version_number = None
    if _get_success(['cat', 'VERSION'], cwd=cwd):
        version_number = _check_output(['cat', 'VERSION'], cwd=cwd)
    return version_number

def is_versionable(fullpath):
    return (os.path.exists(fullpath) and
            os.path.isdir(fullpath) and
            _is_git_repo(cwd=fullpath))

def git_version(no_fetch=False, cwd=None):
    # If requested, attempt to fetch remote
    if not no_fetch:
        command = ['git', 'fetch']
        logger.info('Running %s in %s', ' '.join(command), cwd)
        fetch_success = _get_success(command, cwd=cwd)

    branch_name = _check_output(['git', 'name-rev', 'HEAD', '--name-only'], cwd=cwd)
    short_hash = _check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=cwd)

    # Does this branch have a remote equivalent at origin?
    symbolic_ref = _check_output(['git', 'symbolic-ref', '--q', 'HEAD'], cwd=cwd)
    remote_branch = _check_output(['git', 'for-each-ref', '--format=%(upstream:short)', symbolic_ref], cwd=cwd)
    has_remote_branch = _get_success(['git', 'rev-parse', '--verify', remote_branch], cwd=cwd)
    if has_remote_branch:
        # If so, how does the local committed state differ from the remote state?
        additional_remote_commits = _check_output(['git', 'log', '{}..{}'.format(
            branch_name, remote_branch), '--decorate', '--oneline'], cwd=cwd)
        additional_local_commits = _check_output(['git', 'log', '{}..{}'.format(
            remote_branch, branch_name), '--decorate', '--oneline'], cwd=cwd)
    else:
        additional_remote_commits = ''
        additional_local_commits = ''

    uncommitted_changes = _check_output(['git', 'status', '--porcelain'], cwd=cwd)
    submodules = _check_output(['git', 'submodule'], cwd=cwd)

    # Build a string to print out!
    version_string = ''
    if no_fetch:
        version_string += '{} {} (Not fetched)\n'.format(branch_name, short_hash)
    else:
        if fetch_success:
            version_string += '{} {} (Fetched)\n'.format(branch_name, short_hash)
        else:
            version_string += '{} {} (Failed to fetch)\n'.format(branch_name, short_hash)
    if len(additional_remote_commits) > 0:
        for s in additional_remote_commits.split('\n'):
            version_string += 'Unmerged remote: {}\n'.format(s)
    if len(additional_local_commits) > 0:
        for s in additional_local_commits.split('\n'):
            version_string += 'Unpushed local: {}\n'.format(s)
    if len(uncommitted_changes) > 0:
        version_string += '{}\n'.format(uncommitted_changes)
    if len(submodules) > 0:
        for s in submodules.split('\n'):
            version_string += 'Submodule: {}\n'.format(s)

    return version_string.strip()
