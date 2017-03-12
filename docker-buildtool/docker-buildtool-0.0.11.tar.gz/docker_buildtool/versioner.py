import os
import logging
import yaml

from pathlib import Path
from docker_buildtool import docker_build, dockerfile, error, utils, git_version

logger = logging.getLogger(__name__)

def path(*args):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), *args))

class Versioner(object):
    def __init__(self, dockerfile):
        self.dockerfile = dockerfile

    def run(self, no_fetch):
        # Collect all the paths to version
        paths = []
        if os.path.exists(self.dockerfile):
            spec = dockerfile.DockerfileBuildSpec(self.dockerfile)
            for include in spec.include:
                fullpath = os.path.join(spec.build_root, include.path)
                paths.append(fullpath)
        else:
            logger.info("Getting versions of global dependencies. cd into a specific project directory (or point at the project Dockerfile with -f) to also capture versions of dependencies for that project.")

        with open(path('./autopull.yml')) as f:
            autopull = yaml.load(f)
        for item, spec in autopull.items():
            repo_path = os.path.join(path('../..'), item)
            paths.append(repo_path)

        # Version the paths, trying not to duplicate work
        versions = {}
        for p in paths:
            if not os.path.exists(p):
                versions[p] = "Does not exist"
            else:
                if git_version.is_versionable(p):
                    name = git_version.repo_name(cwd=p)
                    if name in versions:
                        logger.debug('Path %s already versioned under name %s', p, name)
                    else:
                        versions[name] = git_version.git_version(no_fetch=no_fetch, cwd=p)

                    version_number = git_version.version_number(cwd=p)
                    if version_number is not None:
                        if 'VERSION' not in versions[name]:
                            versions[name]['VERSION'] = version_number

                else:
                    logger.debug('Path %s is not versionable', p)

        return versions
