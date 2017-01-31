"""
Tool that invokes the named script from a project local bin directory.

The scripts are called with the project path as the first argument.
"""

import logging

from menhir.tool import Tool
from menhir.tool_utils import OK, FAIL, NOTHING_TO_DO, tool_env, working_dir

log = logging.getLogger(__name__)


def tool():
    return Script()


class Script(Tool):

    def is_using_tool(tool, path, info):
        from os.path import exists, join
        return exists(join(path, 'bin'))

    def dependencies(tool, path):
        return []

    def add_arg_parser(tool, parser):
        parser.description = "Invoke scripts from project bin sub-directory"
        parser.add_argument(
            'script_name',
            metavar='script-name',
            help='script to invoke from bin directory'
        )
        parser.add_argument('args', nargs='*', help='script arguments')

    def execute_build_phase(tool, path, info, args):
        """Execute a build phase."""
        import os
        import os.path
        import subprocess

        with working_dir(path):
            script_file = os.path.join('bin', args.script_name)
            if os.access(script_file, os.X_OK):
                log.info('Running script bin/%s in %s', args.script_name, path)

                if args.only_if_changed and not (
                        info.get('changed') or
                        info.get('changed_dependents')
                ):
                    return OK

                env = tool_env()
                if args.all:
                    env['MENHIR_ALL'] = "1"
                if info.get('changed'):
                    env['MENHIR_CHANGED'] = "1"
                if info.get('changed_dependents'):
                    env['MENHIR_CHANGED_DEPENDENTS'] = "1"
                if info.get('changed_dependees'):
                    env['MENHIR_CHANGED_DEPENDEES'] = "1"

                result = subprocess.call(
                    [script_file] + args.args,
                    env=env,
                )
                log.debug('Script %s result: %s', args.script_name, result)
                if result:
                    return FAIL
                return OK
            else:
                log.debug('No script for build phase %s', args.script_name)
                return NOTHING_TO_DO
