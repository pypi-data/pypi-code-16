import os
import shutil
from uuid import uuid4
from bucketlist.errors import BucketlistError
from bucketlist.decorators import dumptime


COMPLETED_STR = 'complete'

def generate_id():
    return str(uuid4())


@dumptime
def validate_init(folder_path):
    if os.path.isfile(folder_path) == True:
        raise BucketlistError("A file already exists at {}. Please give a suitable data directory and continue.".format(folder_path), error_code="file_instead_of_folder")

    if os.path.isdir(folder_path) == False:
        raise BucketlistError("Folder does not exist at {}.\n    Please run `bucket-list init`".format(folder_path), error_code="folder_does_not_exist")


@dumptime
def category_exists(folder_path, category_name):
    return os.path.isdir(os.path.join(folder_path, category_name))


@dumptime
def create_category(folder_path, category_name):
    return os.mkdir(os.path.join(folder_path, category_name))


@dumptime
def create_item(folder_path, category_name, message):
    item_id = generate_id()
    file_name = "{}".format(item_id)
    with open(os.path.join(folder_path, category_name, item_id), 'w') as f:
        f.write(message)
    return item_id


@dumptime
def get_items(folder_path, category_name, completed=False):
    files = os.listdir(os.path.join(folder_path, category_name))

    pending_items = []
    completed_items = []

    for file_name in files:
        with open(os.path.join(folder_path, category_name, file_name)) as f:
            message = f.read()
            if file_name.endswith('.{}'.format(COMPLETED_STR)):
                completed_items.append({
                    'id': file_name.split('.')[0],
                    'message': message
                })
            else:
                pending_items.append({
                    'id': file_name,
                    'message': message
                })

    if completed == True:
        return completed_items
    return pending_items


@dumptime
def get_categories(folder_path):
    return os.listdir(folder_path)


@dumptime
def update_item(folder_path, category_name, item_id, completed=True):
    filepath = os.path.join(folder_path, category_name, item_id)

    item_pending_file = filepath
    item_completed_file = "{}.{}".format(filepath, COMPLETED_STR)

    message = None
    if completed == True and os.path.isfile(item_pending_file) == True:
        with open(item_pending_file, 'r') as f:
            message = f.read()
        os.rename(item_pending_file, item_completed_file)
    elif completed == False and os.path.isfile(item_completed_file) == True:
        with open(item_completed_file, 'r') as f:
            message = f.read()
        os.rename(item_completed_file, item_pending_file)
    else:
        raise BucketlistError("Item with id '{}' does not exist".format(item_id))

    return {
        'id': item_id,
        'message': message,
        'completed': completed
    }


@dumptime
def get_item(folder_path, category_name, item_id):
    filepath = os.path.join(folder_path, category_name, item_id)

    item_pending_file = filepath
    item_completed_file = "{}.{}".format(filepath, COMPLETED_STR)

    message = None
    if os.path.isfile(item_pending_file) == True:
        with open(item_pending_file, 'r') as f:
            message = f.read()
    elif os.path.isfile(item_completed_file) == True:
        with open(item_completed_file, 'r') as f:
            message = f.read()
    else:
        return None

    return {
        'id': item_id,
        'message': message,
        'completed': os.path.isfile(item_completed_file) == True
    }


@dumptime
def delete_folder(folder_path):
    shutil.rmtree(folder_path)


@dumptime
def folder_exists(folder_path):
    return os.path.isdir(folder_path)


@dumptime
def file_exists(file_path):
    return os.path.isfile(file_path)


@dumptime
def create_folder(folder_path):
    os.makedirs(folder_path)
