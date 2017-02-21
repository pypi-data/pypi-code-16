# -*- coding: utf-8 -*-
from ..core.utils import try_subprocess_call_and_return
from ..domain.vendor import GitError


def _execute_command(command):
    is_success, response = try_subprocess_call_and_return(command)
    if not is_success:
        raise GitError('"%s" failed with error code: %s' % (' '.join(command), response))
    return response


def get_current_branch():
    command = ['git', 'rev-parse', '--abbrev-ref', 'HEAD']
    return _execute_command(command)


def get_current_commit():
    command = ['git', 'rev-parse', 'HEAD']
    return _execute_command(command)
