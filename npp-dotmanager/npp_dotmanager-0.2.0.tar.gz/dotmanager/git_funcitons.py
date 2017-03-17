# Functions related to git

from os import chdir, getcwd

from .command_calling import call_command


def git_clone(source_url, dest_dir):
    "Calls git clone on source url and puts it in the destination directory. \
    Url and path should be checked before calling this function. Path should \
    be absolute. Returns the stdout and stderr."
    stdout, stderr = call_command(
        'git clone {0} {1}'.format(source_url, dest_dir))
    return stdout, stderr


def git_commit(dest_dir, message='', branch="master"):
    "Changes current dir to destination dir, calls `git add .` then `git ci` \
    or `git ci -m 'message'`, then changes back to the original dir."
    curr_dir = getcwd()
    chdir(dest_dir)
    stdout, stderr = call_command('git status')
    # print(stdout)
    stdout, stderr = call_command('git add .')
    # print("After git add called:\n", stdout, stderr)
    stdout, stderr = call_command('git status')
    # print(stdout)
    if message == '':
        stdout, stderr = call_command(
            'git commit -m "Backup from dotmanager.py"')
    else:
        stdout, stderr = call_command('git commit -m "{0}"'.format(message))

    # print('After commit:\n', stdout, stderr)

    out, _ = call_command('git push origin {0}'.format(branch))
    chdir(curr_dir)
