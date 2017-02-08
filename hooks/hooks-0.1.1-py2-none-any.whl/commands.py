import string
import os
import stat


def _ensure_cwd_is_a_git_repo():
    """Is the current working directory a git repo?"""
    dot_git = os.path.join(os.getcwd(), '.git')
    if not (os.path.exists(dot_git) and os.path.isdir(dot_git)):
        raise RuntimeError('Must be in a git repository')


def _generate_hook(src_content, dest, use_force):
    if os.path.exists(dest) and not use_force:
        user_input = raw_input('{} exists. \n'
                               'Do you want to overwrite it? [Y/n] '.format(dest))
        if user_input.lower() == 'n':
            return False
    with open(dest, 'w') as fh:
        fh.write(src_content)

    os.chmod(dest, stat.S_IXUSR | stat.S_IREAD | stat.S_IWRITE)
    return True


def install(args):
    """\
Install the hooks into the current git repository.

Usage:
    install [-f]

Options:
    -f  Overwrite without prompt when the hook already exists."""
    use_force = args.get('-f', False)
    _ensure_cwd_is_a_git_repo()
    git_hook_directory = os.path.join(os.getcwd(), '.git', 'hooks')

    for hook in ('prepare-commit-msg', 'commit-msg'):
        source = os.path.join(os.path.dirname(__file__), 'githooks', 'generic_hook_tmpl')
        with open(source, 'r') as fh:
            tmpl = string.Template(fh.read())
            source_content = tmpl.substitute(hook_type=hook)
        dest = os.path.join(git_hook_directory, hook)
        if _generate_hook(source_content, dest, use_force):
            print('{} hook installed'.format(hook))


def update(args):
    pass


def ls(args):
    pass
