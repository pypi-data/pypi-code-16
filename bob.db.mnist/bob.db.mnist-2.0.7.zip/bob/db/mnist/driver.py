#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# @date: Wed May 8 19:15:47 CEST 2013
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Commands the MNIST database can respond to.
"""

import os
import sys
from bob.db.base.driver import Interface as BaseInterface


def download_mnist(self):
  # Hack that will download the mnist database

  import pkg_resources
  import bob.db.mnist
  db_folder = pkg_resources.resource_filename(__name__, '') # Defining a folder for download
  db = bob.db.mnist.Database(data_dir=db_folder) # Downloading
  del db

class Interface(BaseInterface):

  def name(self):
    return 'mnist'

  def version(self):
    import pkg_resources  # part of setuptools
    return pkg_resources.require('bob.db.%s' % self.name())[0].version

  def files(self):
    return ()

  def type(self):
    return 'binary'

  def add_commands(self, parser):

    from . import __doc__ as docs
    from bob.db.base.driver import download_command
    subparsers = self.setup_parser(parser, "MNIST database", docs)

    parser = download_command(subparsers)
    parser.set_defaults(func=download_mnist)


