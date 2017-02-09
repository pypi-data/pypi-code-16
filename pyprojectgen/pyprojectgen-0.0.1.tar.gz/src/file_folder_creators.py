import os

def create_folder(path):
    """Creates a folder is it does not exist."""
    if not os.path.exists(path):
        os.mkdir(path)

