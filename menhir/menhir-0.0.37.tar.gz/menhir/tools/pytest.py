"""
The pytest tool invokes pytest based tests.
"""
import logging

from menhir.tool import Tool
from menhir.tool_utils import (
    OK,
    FAIL,
    NOTHING_TO_DO,
    package_script,
    tool_env,
    working_dir,
)

log = logging.getLogger(__name__)


def tool():
    return PyTest()


class PyTest(Tool):

    def is_using_tool(tool, path, info):
        from os.path import exists, join
        path = join(path, 'setup.cfg')
        if exists(path):
            with open(path, "r") as file:
                data = file.read()
                return 'pytest' in data

    def dependencies(tool, path):
        return []

    def add_arg_parser(tool, parser):
        parser.description = "Invoke pytest based tests"
        parser.add_argument('args', nargs='*', help='pytest arguments')

    def execute_build_phase(tool, path, info, args,):
        """Execute a build phase."""
        import subprocess

        log.info('pytest: %s %s %s', path, info, args)
        if info.get('changed') or info.get('changed_dependents') or args.all:
            log.info('Running pytest in %s', path)
            project_name = info['project-name']
            env = tool_env()
            env['MENHIR_PROJECT'] = project_name
            with package_script("/tools/pytest/test.sh") as f:
                with working_dir(path):
                    res = subprocess.call([f.name] + args.args, env=env)
                    if res:
                        return FAIL
                    return OK
        else:
            return NOTHING_TO_DO
