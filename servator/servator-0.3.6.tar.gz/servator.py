# coding: utf-8

import shutil
import tempfile
import os.path
import zipfile

import click
import requests


SERVATOR_API_UPLOAD_ENDPOINT = 'http://serve.janitorrb.com/api/upload'


@click.group()
def cli():
    pass


@cli.command()
@click.argument('path-to-serve', type=click.Path(exists=True))
def serve(path_to_serve):
    serve_archive = get_serve_archive(path_to_serve)
    serve_url = send_serve(serve_archive)
    click.echo(click.style('Your serve url: ', fg='blue'), nl=False)
    click.echo(click.style(serve_url, fg='red', underline=True))


def send_serve(serve_archive):
    files = {'serve': (serve_archive, open(serve_archive, 'rb'), 'application/zip')}
    response = requests.post(SERVATOR_API_UPLOAD_ENDPOINT, files=files)
    if response.status_code != 200:
        raise click.ClickException('Servator server error. Response code: %s' % response.status_code)
    return get_serve_url_from_response(response)


def get_serve_archive(path_to_serve):
    if os.path.isdir(path_to_serve):
        return make_dir_archive(path_to_serve)
    return make_file_archive(path_to_serve)


def make_dir_archive(path_to_serve):
    serve_zip = tempfile.NamedTemporaryFile()
    shutil.make_archive(serve_zip.name, 'zip', path_to_serve)
    return serve_zip.name + '.zip'


def make_file_archive(path_to_serve):
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    with zipfile.ZipFile(tmp_file, 'w') as zip_file:
        zip_file.write(path_to_serve)
    return tmp_file.name


def get_serve_url_from_response(response):
    response_json = response.json()
    return response_json['result']['serve_url']


if __name__ == '__main__':
    cli()
