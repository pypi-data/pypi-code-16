import os

# FILE_NAME = f'.{os.sep}resources{os.sep}build_number.txt'
FILE_NAME = '.{os_sep}resources{os_sep}build_number.txt'.format(os_sep=os.sep)


def update_version():
    with open(FILE_NAME) as file:
        file_str = file.read()

    file_str_parts = file_str.split('.')
    file_str_parts[-1] = str(int(file_str_parts[-1]) + 1)

    with open(FILE_NAME, "w") as file:
        file.write('.'.join(file_str_parts))


def get_version():
    try:
        with open(FILE_NAME) as file:
            return file.read()
    except FileNotFoundError:
        return '1.0.0'
