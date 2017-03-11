import click
import sys

import time

from py_build_server.lib import ExtendedRepo
from py_build_server.config import Config
from py_build_server.lib.twine_extentions import UploadCall, Twine


@click.command()
def cli():
    config = Config()
    while True:
        for repo in ExtendedRepo.build_repos_from_config(config):
            check_repo(repo)
            click.echo('waiting')
            time.sleep(repo.config.fetch_frequency * 60)


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
    twine_call = UploadCall(repo)
    Twine(repo).upload(twine_call, latest_tag)


if __name__ == '__main__':
    cli(sys.argv[1:])
