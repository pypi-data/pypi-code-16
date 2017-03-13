from glob import glob
from invisibleroads_macros.disk import get_file_extension
from invisibleroads_posts.views import expect_param
from os import rename
from os.path import basename, join
from pyramid.httpexceptions import HTTPBadRequest, HTTPNotFound
from pyramid.session import check_csrf_origin, check_csrf_token
from shutil import copyfileobj

from .models import Upload


def add_routes(config):
    config.add_route('files.json', '/files.json')

    config.add_view(
        receive_file,
        permission='upload-file',
        renderer='json',
        request_method='POST',
        require_csrf=False,
        route_name='files.json')


def receive_file(request):
    if request.authenticated_userid:
        check_csrf_origin(request) and check_csrf_token(request)
    try:
        field_storage = request.POST['files[]']
    except KeyError:
        raise HTTPBadRequest
    source_file = field_storage.file
    source_name = basename(field_storage.filename)
    source_extension = get_file_extension(source_name)

    settings = request.registry.settings
    upload_folder = Upload.spawn_folder(request.data_folder, settings[
        'upload.id.length'], request.authenticated_userid)
    upload_path = join(upload_folder, 'raw' + source_extension)

    temporary_path = join(upload_folder, 'temporary.bin')
    with open(temporary_path, 'wb') as temporary_file:
        copyfileobj(source_file, temporary_file)
    rename(temporary_path, upload_path)

    open(join(upload_folder, 'name.txt'), 'wt').write(source_name)
    return {
        'upload_id': basename(upload_folder),
    }


def get_upload_from(request):
    upload_id = expect_param('upload_id', request.params)
    try:
        upload = get_upload(request, upload_id)
    except IOError:
        raise HTTPNotFound({'upload_id': 'bad'})
    return upload


def get_upload(request, upload_id):
    upload = Upload(id=upload_id, owner_id=request.authenticated_userid)
    upload.folder = upload.get_folder(request.data_folder)
    try:
        upload.path = glob(join(upload.folder, 'raw*'))[0]
    except IndexError:
        raise IOError
    upload.name = open(join(upload.folder, 'name.txt')).read()
    return upload
