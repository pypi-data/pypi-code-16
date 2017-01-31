"""
Pyenv based tool for menhir.

The ``pyenv`` tool provides the ``virtualenv`` target to create a
virtualenv for each of the repository's projects.  The virtualenv is
loaded with all the project's dependencies as specified in
``requirements*.txt``.
"""
import logging

from menhir.tool import Tool
from menhir.tool_utils import OK, FAIL, NOTHING_TO_DO, tool_env, working_dir

log = logging.getLogger(__name__)


def tool():
    return Pyenv()


class Pyenv(Tool):

    def is_using_tool(tool, path, info):
        from glob import glob
        from os.path import exists, join
        setup_py = join(path, 'setup.py')
        requirements = join(path, 'requirements*.txt')
        files = glob(requirements)
        return exists(setup_py) and bool(files)

    def dependencies(tool, path):
        return []

    def add_arg_parser(tool, parser):
        parser.description = "Manage project specific pyenv virtualenvs"
        parsers = parser.add_subparsers(help="pyenv commands", dest='phase')
        parsers.add_parser(
            'virtualenv',
            help='Build a pyenv virtualenv with the projects dependencies'
        )

    def execute_build_phase(tool, path, info, args,):
        """Execute a build phase."""
        import subprocess
        from menhir.tool_utils import package_script

        if args.phase == 'virtualenv':
            if (
                    args.all or
                    info.get('changed') or
                    info.get('changed_dependents') or
                    (info.get('changed_dependees') and
                     not args.only_if_changed)
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
