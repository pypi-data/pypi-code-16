
import os
import sys
import shutil
import inspect
import fnmatch

__author__ = u'Oli Davis'
__copyright__ = u'Copyright (C) 2016 Oli Davis'


def get_files(directory,
              pattern=u'*',
              recursive=False,
              include_path=True):

    """ Get all files of type from directory

    :param directory:       Directory to find files in.
    :param pattern:         str: extension of files to find e.g '*' for all files and folders,
                                                                '*.*' for all files
                                                                '*.json' for all json files,
                                                                'A*.*' for all files beginning with 'A'.
    :param recursive:       bool: True = recursively search sub-folders,
                                  False = ignore sub-folders.
    :param include_path:    bool: True = full path to file,
                                  False = only file names returned.

    :return list
    """

    # TODO: Add support for finding directories in recursive mode!

    output = []

    if recursive:
        for root, dir_names, file_names in os.walk(directory):
            for f in fnmatch.filter(file_names, pattern):
                output.append(os.path.join(root, f) if include_path else f)

    else:
        for f in fnmatch.filter(os.listdir(directory), pattern):
            output.append(os.path.join(directory, f) if include_path else f)

    return output


def get_files_dict(directory,
                   output_dict,
                   file_type=u'.json'):

    """ Get all files of type from directory

    :param directory:   Directory to find files in.
    :param output_dict: dict object to add files to.
    :param file_type:   str: extension of files to find e.g '.json' for all json files, '' for all files.
    """

    preview_files = os.listdir(directory)

    if preview_files:
        for f in preview_files:
            if f.endswith(file_type):
                fn, _ = f.split(u'.')
                output_dict[fn] = os.path.join(directory, f)


def get_ordered_files(folder,
                      extension_filter=u'',
                      include_path=True):

    # TODO: Write unittests

    # TODO: convert to calling get_files
    filenames = [(os.path.join(folder, filename) if include_path else filename)
                 for filename in os.listdir(folder)
                 if filename.endswith(extension_filter)]

    filenames.sort()
    return filenames


pre_patched_copyfileobj = None


def make_windows_file_copy_faster(length = 16 * 1024 * 1024):
    u"""
    monkey patch copy buffer size for faster copy on Windows!
    default is 16KB, increase to 16MB

    :param length: copy buffer length

    """
    global pre_patched_copyfileobj

    if sys.platform != u'win32':
        return

    if length in inspect.getargspec(shutil.copyfileobj).defaults:
        # already patched
        return

    if not pre_patched_copyfileobj:
        pre_patched_copyfileobj=shutil.copyfileobj

    def copyfileobj(fsrc,
                    fdst,
                    length = 16 * 1024 * 1024):
        pre_patched_copyfileobj(fsrc=fsrc,
                                fdst=fdst,
                                length=length)

    shutil.copyfileobj = copyfileobj
