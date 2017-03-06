import click
from .common.transfer import download_with_progressbar, upload_with_progressbar


@click.command()
@click.argument('url')
@click.option('--output', '-o', default=None)
@pass_data
def download(data, url, output):
    """
    proof of concept to show the progress bar
    """
    download_with_progressbar(data, url, output)


@click.command()
@click.argument('url')
@click.argument('filename')
@pass_data
def upload(data, url, filename):
    """
    proof of concept to show the progress bar
    """
    upload_with_progressbar(data, url, filename)
