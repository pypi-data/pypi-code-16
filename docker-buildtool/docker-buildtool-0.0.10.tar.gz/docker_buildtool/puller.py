import os
import logging
import yaml

from pathlib import Path
from docker_buildtool import docker_build, dockerfile, error, utils

logger = logging.getLogger(__name__)

def path(*args):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), *args))

class Puller(object):
    def __init__(self, dockerfile):
        self.dockerfile = dockerfile

    def run(self, dryrun):
        if os.path.exists(self.dockerfile):
            spec = dockerfile.DockerfileBuildSpec(self.dockerfile)
            spec.run_setup(dryrun)

            for include in spec.include:
                if not include.installable:
                    continue
                include.install(dryrun=dryrun, build_root=spec.build_root)
        else:
            logger.info("\n\nPulling global dependencies. cd into a specific project directory (or point at the project Dockerfile with -f) to also pull dependencies for that project.\n\n")

        # Pull in the local repo
        utils.execute_command(dryrun, ['git', 'pull', '--rebase'])

        with open(path('./autopull.yml')) as f:
            autopull = yaml.load(f)

        for name, spec in autopull.items():
            # TODO: DRY this up
            repo_path = os.path.join(path('../..'), name)
            if not os.path.exists(repo_path):
                utils.execute_command(dryrun, ['git', 'clone', spec['git']], cwd=str(Path(repo_path).parent))

            # Pull in these tooling repos
            utils.execute_command(dryrun, ['git', 'pull', '--rebase'], cwd=repo_path)
            utils.execute_command(dryrun, ['git', 'submodule', 'update', '--init', '--recursive'], cwd=repo_path)
            # Installed executables become unhappy when their
            # version changes, which means we need to
            # reinstall them.
            #
            # Also just make sure people haven't installed the Pypi
            # version of things.
            #
            # TODO: figure out how to bring this back. Most setups
            # probably would require 'sudo'.
            #
            # utils.execute_command(dryrun, spec['setup'], cwd=repo_path, shell=True)
