"""
Pyenv based tool for menhir.

The ``pyenv`` tool provides the ``virtualenv`` target to create a
virtualenv for each of the repository's projects.  The virtualenv is
loaded with all the project's dependencies as specified in
``requirements*.txt``.
"""
import argparse
import logging

from menhir.tool import Tool
from menhir.tool_utils import OK, FAIL, NOTHING_TO_DO, tool_env, working_dir

log = logging.getLogger(__name__)


def tool():
    return Pyenv()


class Pyenv(Tool):

    def dir_info(tool, path, info):
        from glob import glob
        from os.path import exists, join
        setup_py = join(path, 'setup.py')
        requirements = join(path, 'requirements*.txt')
        files = glob(requirements)
        has_requirements = exists(setup_py) and bool(files)
        return {
            'project_recognised': has_requirements,
            'can_run': has_requirements,
        }

    def dependencies(tool, path):
        return []

    def arg_parser(tool, **kwargs):
        return parser(**kwargs)

    def execute_tool(tool, path, info, args,):
        """Execute a build phase."""
        import subprocess
        from menhir.tool_utils import package_script

        if args.phase == 'virtualenv':
            if (
                    'changed' not in info or
                    info['changed'].get('self') or
                    info['changed'].get('dependents')
            ):
                log.info('Running pyenv requirements in %s', path)

                env = tool_env()

                with package_script("/tools/pyenv/requirements.sh") as f:
                    with working_dir(path):
                        res = subprocess.call(
                            [f.name, path, info['project-name']],
                            env=env,
                        )
                        if res:
                            return FAIL
                        return OK
            else:
                log.info('not running pyenv requirements in %s', path)
                return OK
        else:
            return NOTHING_TO_DO


def parser(**kwargs):
    parser = argparse.ArgumentParser(
        description="Manage project specific pyenv virtualenvs",
        **kwargs
    )
    parsers = parser.add_subparsers(help="pyenv commands", dest='phase')
    parsers.add_parser(
        'virtualenv',
        help='Build a pyenv virtualenv with the projects dependencies'
    )
    return parser
