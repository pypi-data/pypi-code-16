from bucketlist.errors import BucketlistError
from bucketlist.decorators import dumptime
from bucketlist.providers.wunderlist import WRequests


DUMMY_LIST_NAME = 'Xc2dsaNhds'


@dumptime
def get_folder(folder_name):
    folder_id = None

    all_folders = WRequests.get('https://a.wunderlist.com/api/v1/folders')
    for f in all_folders:
        if f.get('title') == folder_name:
            folder_id = f.get('id')
            break

    if folder_id is None:
        raise BucketlistError("Folder with name '{}' does not exist on Wunderlist".format(folder_name))

    return WRequests.get('https://a.wunderlist.com/api/v1/folders/{}'.format(folder_id))


@dumptime
def get_lists(folder):
    l = []
    for list_id in folder.get('list_ids'):
        x = {}
        try:
            x = WRequests.get('https://a.wunderlist.com/api/v1/lists/{}'.format(list_id))
        except BucketlistError as e:
            if hasattr(e, 'error_code') and getattr(e, 'error_code') == 'permission_error':
                continue
            else:
                raise e

        if len(x) == 0 or x.get('title') == DUMMY_LIST_NAME:
            continue

        l.append(x)

    return l


@dumptime
def get_list(folder, list_name):
    lists = [l for l in get_lists(folder) if l.get('title') == list_name]
    if len(lists) > 0:
        return lists[0]

    raise BucketlistError("List with name '{}' does not exist on Wunderlist".format(list_name))


@dumptime
def delete_list(list_id):
    l = WRequests.get('https://a.wunderlist.com/api/v1/lists/{}'.format(list_id))
    params = {
        'revision': l.get('revision')
    }
    is_deleted = WRequests.delete('https://a.wunderlist.com/api/v1/lists/{}'.format(list_id), params=params)

    if is_deleted is False:
        raise BucketlistError("List with ID '{}' could not be deleted on Wunderlist".format(list_id))


@dumptime
def get_tasks(wlist, completed=False):
    params = {
        'list_id': wlist.get('id'),
        'completed': completed
    }
    return WRequests.get('https://a.wunderlist.com/api/v1/tasks', params=params)


@dumptime
def get_task(task_id):
    try:
        task = WRequests.get('https://a.wunderlist.com/api/v1/tasks/{}'.format(task_id))
    except BucketlistError as e:
        if e.error_code == 'not_found':
            return None
        raise e
    else:
        return task


@dumptime
def update_task(task_id, completed=None):
    task = get_task(task_id)

    payload = {
        'revision': task.get('revision'),
        'completed': completed
    }
    return WRequests.patch('https://a.wunderlist.com/api/v1/tasks/{}'.format(task_id), json=payload)


@dumptime
def create_folder(folder_name, list_ids):
    folder = WRequests.post('https://a.wunderlist.com/api/v1/folders', json={
        'title': folder_name,
        'list_ids': list_ids
    })
    return get_folder(folder_name)


@dumptime
def create_list(folder, list_name):
    wlist = WRequests.post('https://a.wunderlist.com/api/v1/lists', json={
        'title': list_name
    })
    if folder:
        resp = WRequests.patch('https://a.wunderlist.com/api/v1/folders/{}'.format(folder.get('id')), json={
            'list_ids': folder.get('list_ids') + [wlist.get('id')],
            'revision': folder.get('revision')
        })
    return wlist


@dumptime
def create_dummy_list():
    wlist = WRequests.post('https://a.wunderlist.com/api/v1/lists', json={
        'title': DUMMY_LIST_NAME
    })
    return wlist


@dumptime
def create_task(wlist, message):
    task = WRequests.post('https://a.wunderlist.com/api/v1/tasks', json={
        'list_id': wlist.get('id'),
        'title': message,
        'completed': False
    })
    return task
