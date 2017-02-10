__author__ = 'Ian Davis'

import cPickle
import glob
import os
import sys
import subprocess
import shutil
from contextlib import contextmanager


KILOBYTES = 1024
MEGABYTES = 1024 * KILOBYTES


class NoArgumentError(Exception):
    pass


class InvalidDirectoryError(Exception):
    def __init__(self, path):
        self.message = '{path} is not a valid directory'.format(path=path)

    def __str__(self):
        return self.message


class NoDatabaseError(Exception):
    def __init__(self, path):
        self.message = 'No proper Hobart database found under {path}'.format(path=path)

    def __str__(self):
        return self.message


def dump_object(python_object, file_path):
    with open(file_path, 'wb') as binary_file:
        cPickle.dump(python_object, binary_file)


def load_object(file_path):
    with open(file_path, 'rb') as binary_file:
        return cPickle.load(binary_file)


def _format_argument_list(args):
    new_args = []
    for arg in args:
        new_args.append(str(arg))

    return new_args


def shell_command(args, console_window=False):
    if not args:
        raise NoArgumentError("No command or arguments supplied")

    formatted_args = _format_argument_list(args)
    startup_info = None

    if windows_platform() and not console_window:
        startup_info = subprocess.STARTUPINFO()
        startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup_info.wShowWindow = subprocess.SW_HIDE

    process = subprocess.Popen(formatted_args,
                               cwd=os.getcwd(),
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               startupinfo=startup_info)

    std_out, std_err = process.communicate()
    exit_code = process.returncode

    return exit_code, std_out, std_err


def application_path(script_path=None):
    if not script_path:
        script_path = __file__

    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(script_path)


def make_path(*parts):
    if parts[0].endswith(':') and windows_platform():
        # On NT based systems a separator still needs to follow drive letters ex C:
        # os.path.join does not seem to understand this, so we have to force it to happen by adding os.sep
        # to the list of parts to pass to os.path.join
        list_parts = list(parts)
        list_parts[0] += os.sep
        parts = list_parts

    return os.path.join(*parts)


def make_directory(path):
    if not path:
        return

    if not os.path.exists(path):
        os.mkdir(path)


def working_directory():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)

    return os.getcwd()


def windows_platform():
    return sys.platform == 'win32'


def sys_exit(exit_code):
    sys.exit(exit_code)


def command_line_arguments():
    return sys.argv


def is_file(path):
    return os.path.isfile(path)


def is_directory(path):
    return os.path.isdir(path)


def exists(path):
    return os.path.exists(path)


def list_directory(path):
    if not is_directory(path):
        raise InvalidDirectoryError(path)

    return os.listdir(path)


def list_subdirectories(path):
    filenames = list_directory(path)

    for file_name in filenames:
        full_path = make_path(path, file_name)
        if is_directory(full_path):
            yield full_path


def list_files(path):
    filenames = list_directory(path)
    for file_name in filenames:
        full_path = make_path(path, file_name)
        if is_file(full_path):
            yield full_path


def rename(path, new_file_name=None, prefix=None, suffix=None, new_extension=None):
    old_file_path, old_extension = os.path.splitext(path)
    old_file_name = os.path.basename(old_file_path)
    file_dir = os.path.dirname(old_file_path)

    if not new_file_name:
        new_file_name = old_file_name

    if not new_extension:
        new_extension = old_extension

    if prefix:
        new_file_name = prefix + new_file_name

    if suffix:
        new_file_name += suffix

    new_file_path = os.path.join(file_dir, new_file_name + new_extension)
    os.rename(path, new_file_path)
    return new_file_path


def find_hobart_database(directory):
    if not is_directory(directory):
        raise InvalidDirectoryError(directory)

    hobart_database_name = 'dbft?.db'
    hobart_glob = make_path(directory, hobart_database_name)
    results = glob.glob(hobart_glob)

    if not results or not len(results):
        raise NoDatabaseError(directory)

    return results[-1]


def resource_file(file_name):
    directory = working_directory()
    if 'resources' not in directory:
        directory = make_path(directory, 'resources')

    return make_path(directory, file_name)


def clear_file(file_name):
    with open(file_name, 'w') as text_file:
        text_file.truncate()


@contextmanager
def change_working_directory(path):
    current_directory = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(current_directory)


def filename(path):
    return os.path.basename(path)


def copy_file(original_path, destination_path):
    shutil.copyfile(original_path, destination_path)


def clear_directory(path, exclude_function=None):
    for file_name in list_directory(path):
        filepath = os.path.join(path, file_name)
        if exclude_function and exclude_function(filepath):
            continue

        os.remove(filepath)


def home_directory(user='~'):
    return os.path.expanduser(user)
