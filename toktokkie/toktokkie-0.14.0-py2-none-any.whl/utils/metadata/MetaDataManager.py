u"""
LICENSE:
Copyright 2015,2016 Hermann Krumrey

This file is part of toktokkie.

    toktokkie is a program that allows convenient managing of various
    local media collections, mostly focused on video.

    toktokkie is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    toktokkie is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with toktokkie.  If not, see <http://www.gnu.org/licenses/>.
LICENSE
"""

# imports
from __future__ import with_statement
from __future__ import absolute_import
import os
from typing import List
from io import open


class MetaDataManager(object):
    u"""
    Class that handles the metadata for Media files
    """

    @staticmethod
    def find_recursive_media_directories(directory, media_type = u""):
        u"""
        Finds all directories that include a .meta directory below a given
        directory. If a media_type is specified, only those directories containing a .meta/type file
        with the media_type as content are considered

        In case the given directory does not exist or the current user has no read access,
        an empty list is returned

        :param directory:  The directory to check
        :param media_type: The media type to check for
        :return:           A list of directories that are identified as TV Series
        """
        directories = []

        if not os.path.isdir(directory):
            return []

        # noinspection PyUnboundLocalVariable
        try:
            children = os.listdir(directory)
        except (OSError, IOError):  # == PermissionError
            # If we don't have read permissions for this directory, skip this directory
            return []

        if MetaDataManager.is_media_directory(directory, media_type):
            directories.append(directory)
        else:
            # Parse every subdirectory like the original directory recursively
            for child in children:
                child_path = os.path.join(directory, child)
                if os.path.isdir(child_path):
                    directories += MetaDataManager.find_recursive_media_directories(child_path, media_type)

        return directories

    @staticmethod
    def is_media_directory(directory, media_type = u""):
        u"""
        Checks if a given directory is a Media directory.
        A directory is a Media directory when it contains a .meta directory. It may also contain a file
        called 'type', which contains information about the type of media it contains.

        :param directory:  The directory to check
        :param media_type: The type of media to check for, optional
        :return:           True if the directory is a TV Series directory, False otherwise
        """
        # noinspection PyUnboundLocalVariable
        try:
            if u".meta" in os.listdir(directory):
                if media_type:
                    with open(os.path.join(directory, u".meta", u"type"), u'r') as typefile:
                        stored_media_type = typefile.read().rstrip().lstrip()
                    return stored_media_type == media_type
                else:
                    return True
        except (OSError, IOError):  #
            return False

    @staticmethod
    def generate_media_directory(directory, media_type = u"generic"):
        u"""
        Makes sure a directory is a media directory of the given type

        :param directory:  The directory
        :param media_type: The media type, if not supplied will default to 'generic'
        :raises:           IOError (FileExistsError), if the file exists and is not a directory
        :return:           None
        """
        if not os.path.isdir(directory):
            if os.path.isfile(directory):
                raise IOError()
            else:
                os.makedirs(directory)

        if not MetaDataManager.is_media_directory(directory, media_type):

            for path in [directory, os.path.join(directory, u".meta", u"icons")]:
                if not os.path.isdir(path):
                    os.makedirs(path)

            with open(os.path.join(directory, u".meta", u"type"), u'w') as f:
                f.write(media_type)

    @staticmethod
    def get_media_type(directory):
        u"""
        Determines the media type of a media directory

        :param directory: The directory to check
        :return:          Either the type identifier string, or an empty string
                          if the directory is not a media directory
        """
        if not MetaDataManager.is_media_directory(directory):
            return u""
        else:
            type_file = os.path.join(directory, u".meta", u"type")

            with open(type_file, u'r') as f:
                return f.read().lstrip().rstrip()
