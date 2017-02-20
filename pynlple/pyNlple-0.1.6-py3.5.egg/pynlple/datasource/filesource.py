# -*- coding: utf-8 -*-
from os.path import join
from os import walk
from io import open

import io

from pynlple.exceptions import DataSourceException
from pynlple.module import is_folder, is_file, list_dir, append_paths


class FilePathSource(object):
    """Class for providing json data from json files."""

    def __init__(self, paths, extension_suffix=None):
        self.paths = paths
        self.extension = extension_suffix

    def get_files(self):
        accumulated_paths = list()
        for path in self.paths:
            if is_file(path):
                accumulated_paths.append(path)
            elif is_folder(path):
                files = list_dir(path)
                if self.extension:
                    for file in filter(lambda f: f.endswith(self.extension), files):
                        accumulated_paths.append(append_paths(path, file))
                else:
                    for file in files:
                        accumulated_paths.append(append_paths(path, file))
            else:
                raise DataSourceException('Path {0} does not exist/is neither file nor folder!'.format(path))
        return accumulated_paths

    def __iter__(self):
        for file_ in self.get_files():
            yield file_

    @staticmethod
    def open_file(filepath, encoding='utf8'):
        return open(filepath, 'rt', encoding=encoding)

    @staticmethod
    def iter_folder_filepaths(folderpath, extension_suffix):
        for root, dirs, files in walk(folderpath):
            for file_ in files:
                if file_.endswith(extension_suffix):
                    yield join(root, file_)

    @staticmethod
    def iter_folder_files(folderpath, extension_suffix, encoding='utf8'):
        for filepath in FilePathSource.iter_folder_filepaths(folderpath, extension_suffix):
            yield FilePathSource.open_file(filepath, encoding)
