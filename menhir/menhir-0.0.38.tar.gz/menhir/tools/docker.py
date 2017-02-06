"""
The docker tool provides ``build``, ``push`` and ``publish`` commands.
"""
import argparse
import logging

from menhir.tool import Tool
from menhir.tool_utils import OK, FAIL, NOTHING_TO_DO, tool_env, working_dir

log = logging.getLogger(__name__)


def tool():
    return Docker()


class Docker(Tool):

    def name(arg):
        return "docker"

    def dir_info(tool, path, info):
        from os.path import exists, join
        path = join(path, 'Dockerfile')
        has_dockerfile = exists(path)
        return {
            'project_recognised': has_dockerfile,
            'can_run': has_dockerfile,
        }

    def dependencies(tool, path):
        return []

    def arg_parser(tool, **kwargs):
        return parser(**kwargs)

    def execute_tool(tool, path, info, args,):
        """Execute a build phase."""
        from os.path import exists, join
        from menhir.tool_utils import run_if

        phase_name = args.phase

        dockerfile = join(path, 'Dockerfile')
        repo = info['config'].get('docker', {}).get('repository')

        if not exists(dockerfile):
            log.debug(
                'No Dockerfile %(dockerfile)s',
                {'dockerfile': dockerfile})
            return NOTHING_TO_DO

        run_flag = (
            'changed' not in info or
            info['changed'].get('self') or
            info['changed'].get('dependents')
        )

        if phase_name == 'build':
            with run_if(run_flag, phase_name, path) as flag:
                if flag:
                    return docker_build(path, info, args)
                return OK

        elif phase_name == 'push':
            with run_if(run_flag, phase_name, path) as flag:
                if flag:
                    return docker_push(repo, path, info, args)
                return OK

        elif phase_name == 'publish':
            with run_if(run_flag, phase_name, path) as flag:
                if flag:
                    res = docker_build(path, info, args)
                    if res != OK:
                        return res
                    return docker_push(repo, path, info, args)
                return OK
        else:
            return NOTHING_TO_DO


def parser(**kwargs):
    parser = argparse.ArgumentParser(
        description="Commands to build and push docker images.",
        **kwargs
    )
    parsers = parser.add_subparsers(help="Docker commands", dest='phase')
    parsers.add_parser(
        'build',
        help='Build a docker image from a Dockerfile'
    )
    parsers.add_parser(
        'push',
        help='Push a docker image to a remote repository'
    )
    parsers.add_parser(
        'publish',
        help='Build and push a docker image to a remote repository'
    )
    return parser


def docker_build(path, info, args):
    from menhir.tool_utils import call, package_script
    log.info('Running docker-build in %s', path)

    project_name = info['project-name']

    env = tool_env()
    env['MENHIR_TAG'] = project_name

    with package_script("/tools/docker/docker-build.sh") as f:
        with working_dir(path):
            return call([f.name], env=env,)


def docker_push(repo, path, info, args):
    from menhir.project import branch, image
    from menhir.tool_utils import call, package_script, slugify
    log.info('Running docker-push in %s', path)

    project_name = info['project-name']
    current_branch = branch()
    tag = project_name
    sha_tag = image(info, path)
    if not sha_tag:
        log.error('No remote repository configured to push to.')
        return FAIL
    branch_tag = "%s:%s" % (
        sha_tag.split(':')[0],
        slugify(current_branch, length=40),
    )

    env = tool_env()
    env['MENHIR_TAG'] = tag
    env['MENHIR_BRANCH_TAG'] = branch_tag
    env['MENHIR_SHA_TAG'] = sha_tag

    with package_script("/tools/docker/docker-push.sh") as f:
        with working_dir(path):
            return call([f.name], env=env,)
