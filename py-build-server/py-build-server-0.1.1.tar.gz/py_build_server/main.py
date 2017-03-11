import click
import sys

import time

from py_build_server.lib import ExtendedRepo
from py_build_server.config import Config
from py_build_server.lib.twine_extentions import UploadCall, Twine
from py_build_server.lib.python_daemon import Daemon
from multiprocessing import Process


class PyBuildServer(Daemon):
    def __init__(self, pidfile):
        super(PyBuildServer, self).__init__(pidfile)
        self.config = Config()

    def run(self, *args, **kwargs):
        processes = []
        for repo in ExtendedRepo.build_repos_from_config(self.config):
            p = Process(target=self.check_repo, args=(repo, ))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

    @staticmethod
    def check_repo(repo):
        click.echo('Checking status of {}'.format(repo.name))
        if repo.config.branch is not None:
            if repo.config.branch != str(repo.active_branch):
                raise click.UsageError(
                    'repository is not on the correct branch({} != {})'
                    .format(repo.active_branch, repo.config.branch))

        status = repo.get_status()
        latest_tag = [tag.name for tag in reversed(sorted(repo.tags)) if tag.name != 'origin'][0]
        if status.behind:
            click.echo('pulling latest changes for {repo} from {remote}/{branch}'
                       .format(repo=repo.name,
                               remote=repo.get_remote().name,
                               branch=repo.active_branch.name))

            repo.get_remote().pull()
        Twine(repo).upload(UploadCall(repo.working_dir, repo.config.twine_conf), latest_tag)
        click.echo('waiting {} minutes before checking again'.format(repo.config.fetch_frequency))
        time.sleep(repo.config.fetch_frequency * 60)


if __name__ == '__main__':
    command = sys.argv[1]
    server = PyBuildServer('/etc/py-build-server/pid')
    if command == 'start':
        server.start()

    elif command == 'stop':
        server.stop()

    elif command == 'restart':
        server.restart()

    elif command == 'foreground':
        server.run()
