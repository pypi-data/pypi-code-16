"""
The codecov tool uplods coverage data to ``codecov.io``.
"""
import logging

from menhir.tool import Tool
from menhir.tool_utils import OK, tool_env, working_dir

log = logging.getLogger(__name__)


def tool():
    return Codecov()


class Codecov(Tool):
    def name(arg):
        return "codecov"

    def is_using_tool(tool, path, info):
        from os.path import exists, join
        path = join(path, '.coverage')
        return exists(path)

    def dependencies(tool, path):
        return []

    def add_arg_parser(tool, parser):
        parser.description = "Push coverage metrics to codecov.io"

    def execute_build_phase(tool, path, info, args,):
        """Execute a build phase."""
        import re
        from os import getenv
        from os.path import exists, join
        from menhir.tool_utils import call, package_script

        print('Try Running codecov in %s' % path)
        if (
                info.get('changed') or
                info.get('changed_dependents') or
                args.all
        ):
            log.info('Running codecov in %s', path)

            if not exists(join(path, '.coverage')):
                log.debug('No .coverage in %s', path)
                return OK

            env = tool_env()
            env['MENHIR_PROJECT'] = info['project-name']
            env['MENHIR_CODECOV_FLAGS'] \
                = re.sub(r'\W', "_", info['project-name'])
            env['CODECOV_TOKEN'] = getenv('CODECOV_TOKEN')

            with package_script("/tools/codecov/upload.sh") as f:
                with working_dir(path):
                    return call([f.name], env=env,)
        else:
            log.info('not running codecov in %s', path)
            return OK
