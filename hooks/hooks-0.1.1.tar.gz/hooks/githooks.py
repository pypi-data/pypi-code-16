import re
import functools
import subprocess
from collections import defaultdict


HOOKS = defaultdict(list)


def get_active_hooks(hook_type):
    return HOOKS.get(hook_type, [])


def prepare_commit_msg_hook(fn):
    @functools.wraps(fn)
    def wrapper(temp_msg_file, *args):
        return fn(temp_msg_file, *args)

    HOOKS['prepare-commit-msg'].append(wrapper)
    return wrapper


def commit_msg_hook(fn):
    @functools.wraps(fn)
    def wrapper(temp_msg_file, *args):
        return fn(temp_msg_file, *args)

    HOOKS['commit-msg'].append(wrapper)
    return wrapper


@prepare_commit_msg_hook
def prepend_jira_ticket_id(temp_msg_file, *args):
    """If you name your branch using the following scheme:

        issue-NNNNN-description
        JIRAPROJECT-NNNNN-description

    this prepare_commit_msg hook will prepend your comment message
    with `issue-NNNNN` or `JIRAPROJECT-NNNNN`
    """
    branch_name = subprocess.check_output('git symbolic-ref --short HEAD', shell=True).strip()
    if '-' not in branch_name:
        return True
    parts = branch_name.split('-')
    jira_ticket = '-'.join(parts[:2])
    with open(temp_msg_file, 'r') as fh:
        msg = fh.read()

    msg = '{}: {}'.format(jira_ticket, msg)
    with open(temp_msg_file, 'w') as fh:
        fh.write(msg)

    return True


@commit_msg_hook
def validate_message_starts_with_ticket_id(temp_msg_file, *args):
    """Validate that the first line of the commit message contains a ticket id

    Ticket ids are in the form of issue-NNNNN or JIRAPROJECT-NNNNN
    """
    with open(temp_msg_file, 'r') as fh:
        first_line = fh.readlines()[0]

    m = re.search(r'^\w+\-\d+[:]?\s', first_line)
    if not m:
        print('Commit aborted: '
              'The first line of the commit message should start with the ticket id')
        return False

    return True
