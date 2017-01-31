"""Menhir command line script.

The script is the main user interface for menhir.
"""
from __future__ import print_function  # NOQA

import logging

from menhir import __version__
from menhir.config import default_root_config, parse_root_config
from menhir.utils import multi, method


log = logging.getLogger(__name__)


def main():
    from menhir import root_config
    config = root_config()
    args = parser(config).parse_args()

    if args.verbose and args.log_level != 'DEBUG':
        args.log_level = 'INFO'
    logging.basicConfig(level=args.log_level)

    write_version()
    if args.version:
        print('Menhir %s' % __version__)
    elif args.menhir_command:
        command(config, args,)


def parser(config=parse_root_config(default_root_config())):
    import argparse
    parser = argparse.ArgumentParser(description="""
Menhir is an extensible build tool, that recognises dependencies
between sub-projects in a repository.
""")
    parser.add_argument(
        "--version",
        default=False,
        action='store_const',
        const=True,
        help="Print menhir version and exit",
    )
    parser.add_argument("--from-commit", help="""
Specify the start commit, to base change calculations on.
This can be specified as a single commit, e.g. 3f8e5bb, 3f8e5bb^, head^.
""")
    parser.add_argument(
        "-v", "--verbose",
        default=False,
        action='store_const', const=True,
        help='Provide verbose output (shortcut for log-levl INFO)',
    )
    parser.add_argument(
        "--log-level", default='WARNING',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Set the log level to output"
    )

    subparsers = parser.add_subparsers(
        help='sub-commands',
        dest='menhir_command'
    )

    subparsers.add_parser(
        'info',
        help="Print project information")

    subparsers.add_parser(
        'changed',
        help="Print changed files")

    parser_exec = subparsers.add_parser('exec', help='execute a build tool')
    parser_exec.add_argument(
        "--only-if-changed",
        default=False,
        action='store_const',
        const=True,
        help="Run only if the project itself has changed",
    )
    parser_exec.add_argument(
        "--all",
        default=False,
        action='store_const',
        const=True,
        help="run task on all projects",
    )

    tool_parsers = parser_exec.add_subparsers(help='tools', dest='tool')
    for tool_name, tool in config['tools'].items():
        tool_parser = tool_parsers.add_parser(
            tool_name,
        )
        tool.add_arg_parser(tool_parser)

    return parser


@multi
def command(root_config, args):
    return args.menhir_command


@method(command, 'info')
def info(root_config, args):
    from pprint import pprint
    from menhir import describe_repository
    config = describe_repository(root_config)
    pprint(config, width=80)


@method(command, 'changed')
def changed(root_config, args):
    from pprint import pprint
    from menhir import describe_repository
    config = describe_repository(root_config)
    files = changed_files(config['git_root'], args.from_commit)
    pprint(files, width=80)


@method(command, 'exec')
def exec_tool(root_config, args):
    import sys
    from menhir import (
        apply_tool,
        describe_repository,
        update_for_changed_files,
    )

    config = describe_repository(root_config)
    tool = root_config['tools'][args.tool]

    project_infos = config['project_infos']
    dependencies = config['dependencies']
    root_projects = config['root_projects']
    git_prefix = config['git_prefix']

    files = changed_files(config['git_root'], args.from_commit)
    update_for_changed_files(
        dependencies, project_infos, root_projects, git_prefix, files
    )

    res = apply_tool(
        dependencies,
        project_infos,
        root_projects,
        tool,
        args,
    )

    if res.get('failed'):
        print('Build tool "%s" failed' % args.tool, file=sys.stderr)
        sys.exit(1)


def changed_files(git_root, from_commit):
    """Return the files that have been changed.

    If from_commit is not None, or an implicit from_commit is found
    from CIRCLE_COMPARE_URL, or CIRCLE_SHA1, then return files changed
    since that commit.

    If there are uncommitted files, return them, return the last
    commit's files.
    """
    from menhir.gitutils import (
        files_changed_since,
        head_commit,
        repo,
        uncommited_files,
    )
    git_repo = repo(git_root)

    from_commit = with_implicit_from_commit(from_commit)

    if from_commit:
        log.info("Files from commit: %s", from_commit)
        files = files_changed_since(git_repo, from_commit)['all']
    else:
        uncommited = uncommited_files(git_repo)['all']
        if uncommited:
            files = uncommited
            log.info("Uncommited files")
        else:
            commit = head_commit(git_repo)
            log.info("Last commit files")
            files = files_changed_since(git_repo, str(commit)+"^")

    return files


def with_implicit_from_commit(from_commit):
    """Return any implicit from commit specification.

    Returns the first of the following that is not nil:

    * ``from_commit``
    * the start of the CIRCLE_COMPARE_URL range
    * the commit prior to CIRCLE_SHA1
    """
    import os

    if from_commit:
        return from_commit

    compare_url = os.getenv('CIRCLE_COMPARE_URL')
    if compare_url:
        log.debug('Deriving commit range from %s', compare_url)
        commit_range = compare_url.rsplit('/', 1)[1]
        return commit_range.split('..')[0]

    if os.getenv('CIRCLE_SHA1'):
        sha = os.getenv('CIRCLE_SHA1')
        return sha+"^"


def write_version():
    from menhir import __version__
    with open('.menhir-version', 'w+') as f:
        f.write(__version__)
