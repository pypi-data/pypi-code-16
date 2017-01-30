# --------------------------------------------------------------------------
# Copyright (c) 2016 Digital Sapphire
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the
# following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
# ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
# ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.
# --------------------------------------------------------------------------
from __future__ import unicode_literals
import logging
import os
import re

from dsdev_utils.exceptions import VersionError
from dsdev_utils.helpers import Version
from dsdev_utils.paths import ChDir, remove_any

from pyupdater.utils.exceptions import PackageHandlerError, UtilsError

log = logging.getLogger(__name__)


def parse_platform(name):
    """Parses platfrom name from given string

    Args:

        name (str): Name to be parsed

    Returns:

        (str): Platform name
    """
    log.debug('Parsing "%s" for platform info', name)
    try:
        re_str = r'-(?P<platform>mac|win|nix[6]?[4]?)-'
        data = re.compile(re_str).search(name)
        platform_name = data.groupdict()['platform']
        log.debug('Platform name is: %s', platform_name)
    except AttributeError:
        raise PackageHandlerError('Could not parse platform from filename')

    return platform_name


def remove_previous_versions(directory, filename):
    "Removes previous version of named file"
    if filename is None:
        log.debug('Cleanup Failed - Filename is None')
        return
    log.debug('Filename: %s', filename)

    if directory is None:
        log.debug('Cleanup Failed - Directory is None')
        return
    log.debug('Directory: %s', directory)

    try:
        current_version = Version(filename)
    except (UtilsError, VersionError):  # pragma: no cover
        log.debug('Cleanup Failed: %s - Cannot parse version info.', filename)
        return

    try:
        # We set the full path here because Package() checks if filename exists
        package_info = Package(os.path.join(directory, filename))
    except (UtilsError, VersionError):
        log.debug('Cleanup Failed: %s - Cannot parse package info.',
                  filename)
        return

    if package_info.info['status'] is False:
        log.debug('Not an archive format: %s', package_info.name)
        return

    log.debug('Current version: %s', str(current_version))
    assert package_info.name is not None
    log.debug('Name to search for: %s', package_info.name)
    with ChDir(directory):
        temp = os.listdir(os.getcwd())
        for t in temp:
            log.debug('Checking: %s', t)
            # Only attempt to remove old files of the one we
            # are updating
            if package_info.name not in t:
                log.debug('File does not match name of current binary')
                continue
            else:
                log.debug('Found possible match')
                log.debug('Latest name: %s', package_info.name)
                log.debug('Old name: %s', t)

            try:
                old_version = Version(t)
            except (UtilsError, VersionError):  # pragma: no cover
                log.warning('Cannot parse version info')
                # Skip file since we can't parse
                continue
            log.debug('Found version: %s', str(old_version))

            if old_version < current_version:
                old_path = os.path.join(directory, t)
                log.debug('Removing old update: %s', old_path)
                remove_any(old_path)
            else:
                log.debug('Old version: %s', old_version)
                log.debug('Current version: %s', current_version)


# ToDo: Remove in version 3.0
def cleanup_old_archives(filename=None, directory=None):
    "Removes previous version of named file"
    remove_previous_versions(directory, filename)
# End Todo


class Patch(object):
    """Holds information for patch file.

    Args:

        patch_info (dict): patch information
    """

    def __init__(self, patch_info):
        self.dst_path = patch_info.get('dst')
        self.patch_name = patch_info.get('patch_name')
        self.dst_filename = patch_info.get('package')
        self.ready = self._check_attrs()

    def _check_attrs(self):
        if self.dst_path is not None:
            # Cannot create patch if destination file is missing
            if not os.path.exists(self.dst_path):
                return False
        # Cannot create patch if destination file is missing
        else:
            return False
        # Cannot create patch if name is missing
        if self.patch_name is None:
            return False
        # Cannot create patch is destination filename is missing
        if self.dst_filename is None:
            return False
        return True


class Package(object):
    """Holds information of update file.

    Args:

        filename (str): name of update file
    """
    # Used to parse name from archive filename
    name_regex = re.compile(r'(?P<name>[\w -]+)-[win|mac|nix]')

    def __init__(self, filename):
        self.name = None
        self.version = None
        self.filename = os.path.basename(filename)
        self.file_hash = None
        self.file_size = None
        self.platform = None
        self.info = dict(status=False, reason='')
        self.patch_info = {}
        # seems to produce the best diffs.
        # Tests on homepage: https://github.com/JMSwag/PyUpdater
        # Zip doesn't keep +x permissions. Only using gz for now.
        self.supported_extensions = ['.zip', '.gz']
        # ToDo: May need to add more files to ignore
        self.ignored_files = ['.DS_Store', ]
        self.extract_info(filename)

    def extract_info(self, package):
        """Gets version number, platform & hash for package.

        Args:

            package (str): filename
        """
        package_basename = os.path.basename(package)

        if not os.path.exists(package):
            msg = '{} does not exist'.format(package)
            log.debug(msg)
            self.info['reason'] = msg
            return
        if package_basename in self.ignored_files:
            msg = 'Ignored file: {}'.format(package_basename)
            log.debug(msg)
            self.info['reason'] = msg
            return
        if os.path.splitext(package_basename)[1].lower() not in \
                self.supported_extensions:
            msg = 'Not a supported archive format: {}'.format(package_basename)
            self.info['reason'] = msg
            log.warning(msg)
            return

        log.debug('Extracting update archive info for: %s', package_basename)
        try:
            v = Version(package_basename)
            self.channel = v.channel
            self.version = str(v)
        except VersionError:
            msg = 'Package version not formatted correctly'
            self.info['reason'] = msg
            log.error(msg)
            return
        log.debug('Got version info')

        try:
            self.platform = parse_platform(package_basename)
        except PackageHandlerError:
            msg = 'Package platform not formatted correctly'
            self.info['reason'] = msg
            log.error(msg)
            return
        log.debug('Got platform info')

        self.name = self._parse_package_name(package_basename)
        assert self.name is not None
        log.debug('Got name of update: %s', self.name)
        self.info['status'] = True
        log.debug('Info extraction complete')

    def _parse_package_name(self, package):
        # Returns package name from update archive name
        # Changes appname-platform-version to appname
        # ToDo: May need to update regex if support for app names with
        #       hyphens in them are requested. Example "My-App"
        log.debug('Package name: %s', package)
        basename = os.path.basename(package)

        r = self.name_regex.search(basename)
        try:
            name = r.groupdict()['name']
        except Exception as err:
            self.info['reason'] = str(err)
            name = None

        log.debug('Regex name: %s', name)
        return name
