import click
from click.testing import CliRunner
from zerotk.zops import cli


def test_jenkins_jobs():
    runner = CliRunner()
    result = runner.invoke(cli.main, ['jenkins-jobs', 'create'])
    assert result.output == 'jenkins-jobs create\nERROR: jenkins-jobs: Jobs directory not found.\n'
