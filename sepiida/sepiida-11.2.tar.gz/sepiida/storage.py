import base64
import io
import urllib.parse

import requests

import sepiida.config


class StorageException(Exception):
    pass

class AlreadyUploadedException(StorageException):
    pass

class NotUploadedException(StorageException):
    pass

class NoFileException(StorageException):
    pass

def _auth_header():
    config = sepiida.config.get()
    credentials = 'api:{}'.format(config.sepiida.api_token).encode('utf-8')
    return {'Authorization' : 'Basic {}'.format(base64.b64encode(credentials).decode('utf-8'))}

def upload_link(key, bucket):
    config = sepiida.config.get()
    payload = {
        'bucket'    : bucket,
        'key'       : str(key),
    }
    url = urllib.parse.urljoin(config.sepiida.storage, 'file/')

    if len('{}?filter[key]={}'.format(url, key)) <= 2000:
        response = requests.get('{}?filter[key]={}'.format(url, key), headers=_auth_header())
    else:
        response = requests.get(url, data='filter[key]={}'.format(key), headers=_auth_header())

    if not response.ok:
        raise StorageException('Unknown storage error: {}'.format(response.text))

    resources = response.json()['resources']
    if len(resources) < 1:
        response = requests.post(url, json=payload, headers=_auth_header())
        if not response.ok:
            try:
                errors = response.json()['errors']
                if 'DuplicateKeyError' in [error['code'] for error in errors]:
                    raise AlreadyUploadedException('A file with key {} has already been uploaded'.format(key))
            except (ValueError, KeyError):
                pass
            raise StorageException('Unknown storage error: {}'.format(response.text))
        upload_location = response.headers['upload-location']
    else:
        upload_location = resources[0].get('upload-location')

    if not upload_location:
        raise AlreadyUploadedException('A file with key {} has already been uploaded'.format(key))

    return upload_location

def download_link(key):
    config = sepiida.config.get()
    url = urllib.parse.urljoin(config.sepiida.storage, 'file/')

    if len('{}?filter[key]={}'.format(url, key)) <= 2000:
        response = requests.get('{}?filter[key]={}'.format(url, key), headers=_auth_header())
    else:
        response = requests.get(url, data='filter[key]={}'.format(key), headers=_auth_header())

    if not response.ok:
        raise StorageException('Unknown storage error: {}'.format(response.text))

    resources = response.json()['resources']
    if len(resources) < 1:
        raise NoFileException('A file with key {} does not exist in the database'.format(key))

    download_location = resources[0].get('content')

    if not download_location:
        raise NotUploadedException('A file with key {} has not yet been uploaded'.format(key))

    return download_location


def get_files(keys):
    config = sepiida.config.get()
    url = urllib.parse.urljoin(config.sepiida.storage, 'file/')
    _filter = ','.join(map(str, keys))

    response = requests.get(url, data='filter[key]={}'.format(_filter), headers=_auth_header())
    if not response.ok:
        raise StorageException('Unknown storage error: {}'.format(response.text))

    resources = response.json()['resources']
    file_to_key_map = {resource['key'] : resource for resource in resources}

    return file_to_key_map

def put(key, bucket, content, mimetype):
    upload_location = upload_link(key, bucket)

    response = requests.put(upload_location, data=content, headers={'content-type': mimetype})
    if not response.ok:
        raise StorageException('Unknown storage error: {}'.format(response.text))

def get(key, output_filename=None):
    download_location = download_link(key)

    response = requests.get(download_location)
    if not response.ok:
        raise StorageException('Unknown storage error: {}'.format(response.text))

    if output_filename:
        with open(output_filename, 'wb') as file:
            file.write(response.content)
            return

    return io.BytesIO(response.content)
