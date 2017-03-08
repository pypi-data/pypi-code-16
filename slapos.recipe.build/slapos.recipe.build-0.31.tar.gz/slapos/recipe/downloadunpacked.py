##############################################################################
#
# Copyright (c) 2010 Vifib SARL and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import os
import logging
import shutil
import subprocess
import tarfile
import zc.buildout
import tempfile
import setuptools

TRUE_VALUES = ('yes', 'true', '1', 'on')

class Recipe:

  def calculate_base(self, extract_dir):
    log = logging.getLogger(self.name)
    # Move the contents of the package in to the correct destination
    top_level_contents = os.listdir(extract_dir)
    if self.options['strip-top-level-dir'].strip().lower() in TRUE_VALUES:
      if len(top_level_contents) != 1:
	    log.error('Unable to strip top level directory because there are more '
	              'than one element in the root of the package.')
	    raise zc.buildout.UserError('Invalid package contents')
      base = os.path.join(extract_dir, top_level_contents[0])
    else:
      base = extract_dir
    return base

  def __init__(self, buildout, name, options):
    self.buildout = buildout
    self.name = name
    self.options = options
    self.logger = logging.getLogger(self.name)
    if 'filename' in self.options and 'destination' in self.options:
      raise zc.buildout.UserError('Parameters filename and destination are '
          'exclusive.')
    self.parts = None
    self.destination = self.options.get('destination', None)
    if self.destination is None:
      self.parts = os.path.join(self.buildout['buildout']['parts-directory'],
          self.name)
      self.destination = self.parts
      # backward compatibility with other recipes -- expose location
      options['location'] = os.path.join(self.buildout['buildout'][
        'parts-directory'], self.name)
    options['target'] = self.destination
    options.setdefault('extract-directory', '')

    self.environ = {}
    self.original_environment = os.environ.copy()
    environment_section = self.options.get('environment-section', '').strip()
    if environment_section and environment_section in buildout:
      # Use environment variables from the designated config section.
      self.environ.update(buildout[environment_section])
    for variable in self.options.get('environment', '').splitlines():
      if variable.strip():
        try:
          key, value = variable.split('=', 1)
          self.environ[key.strip()] = value
        except ValueError:
          raise zc.buildout.UserError('Invalid environment variable definition: %s', variable)
    # Extrapolate the environment variables using values from the current
    # environment.
    for key in self.environ:
      self.environ[key] = self.environ[key] % os.environ

  def install(self):
    if self.parts is not None:
      if not os.path.isdir(self.parts):
        os.mkdir(self.parts)
    
    download = zc.buildout.download.Download(self.buildout['buildout'],
        hash_name=True, cache=self.buildout['buildout'].get('download-cache'))
    path, is_temp = download(self.options['url'],
        md5sum=self.options.get('md5sum'))
    extract_dir = tempfile.mkdtemp(self.name)
    self.logger.debug('Created working directory %r' % extract_dir)
    try:
      patch_archive_util()
      # ad-hoc support for .xz and .lz archive
      hdr = file(path).read(6)
      if hdr == '\xfd7zXZ\x00':
        new_path = os.path.join(extract_dir, os.path.basename(path))
        file(new_path, 'w').write(subprocess.check_output(['xzcat', path], env=self.environ))
        setuptools.archive_util.unpack_archive(new_path, extract_dir)
        os.unlink(new_path)
      elif hdr.startswith('LZIP'):
        new_path = os.path.join(extract_dir, os.path.basename(path))
        file(new_path, 'w').write(subprocess.check_output(['lunzip', '-c', path], env=self.environ))
        setuptools.archive_util.unpack_archive(new_path, extract_dir)
        os.unlink(new_path)
      else:
        setuptools.archive_util.unpack_archive(path, extract_dir)
    finally:
      unpatch_archive_util()

    # Delete destination directory if exist
    if os.path.exists(self.destination):
      shutil.rmtree(self.destination)

    # Create destination directory
    if not os.path.isdir(self.destination):
      os.makedirs(self.destination)

    base_dir = extract_dir
    if not self.options.has_key('strip-top-level-dir'):
      directories = os.listdir(extract_dir)
      if len(directories) == 1 and os.path.isdir(os.path.join(extract_dir, directories[0])):
        base_dir = os.path.join(extract_dir, directories[0])
    else:
      base_dir = self.calculate_base(extract_dir)
    extract_dir = os.path.join(base_dir, self.options['extract-directory'])
    for filename in os.listdir(extract_dir):
      dest = os.path.join(self.destination, filename)
      shutil.move(os.path.join(extract_dir, filename), dest)

    shutil.rmtree(extract_dir)
    self.logger.debug('Downloaded %r and saved to %r.' % (self.options['url'],
      self.destination))
    if self.parts is not None:
      return [self.parts]
    else:
      return []
  
  def update(self):
    pass

# Monkey patch to keep symlinks in tarfile
def unpack_tarfile_patched(filename, extract_dir, progress_filter=setuptools.archive_util.default_filter):
    """Unpack tar/tar.gz/tar.bz2 `filename` to `extract_dir`

    Raises ``UnrecognizedFormat`` if `filename` is not a tarfile (as determined
    by ``tarfile.open()``).  See ``unpack_archive()`` for an explanation
    of the `progress_filter` argument.
    """
    try:
        tarobj = tarfile.open(filename)
    except tarfile.TarError:
        raise setuptools.archive_util.UnrecognizedFormat(
            "%s is not a compressed or uncompressed tar file" % (filename,)
        )
    with setuptools.archive_util.contextlib.closing(tarobj):
        # don't do any chowning!
        tarobj.chown = lambda *args: None
        for member in tarobj:
            name = member.name
            # don't extract absolute paths or ones with .. in them
            if not name.startswith('/') and '..' not in name.split('/'):
                prelim_dst = os.path.join(extract_dir, *name.split('/'))

                if member is not None and (member.isfile() or member.isdir() or member.islnk() or member.issym()):
                    final_dst = progress_filter(name, prelim_dst)
                    if final_dst:
                        if final_dst.endswith(os.sep):
                            final_dst = final_dst[:-1]
                        try:
                            # XXX Ugh
                            tarobj._extract_member(member, final_dst)
                        except tarfile.ExtractError:
                            # chown/chmod/mkfifo/mknode/makedev failed
                            pass
        return True

def patch_archive_util():
  setuptools.archive_util.extraction_drivers = (
    setuptools.archive_util.unpack_directory,
    setuptools.archive_util.unpack_zipfile,
    unpack_tarfile_patched,
  )

def unpatch_archive_util():
  setuptools.archive_util.extraction_drivers = (
    setuptools.archive_util.unpack_directory,
    setuptools.archive_util.unpack_zipfile,
    setuptools.archive_util.unpack_tarfile,
  )
