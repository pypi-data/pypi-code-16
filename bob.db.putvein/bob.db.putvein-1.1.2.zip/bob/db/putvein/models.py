#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import os
import bob.io.base
import bob.io.image
import numpy as np


class File(object):
    """ Generic file container """

    def __init__(self, filename, id, mirrored=False):
        self.filename = filename
        self.mirrored = mirrored
        self.client_id = id


    def __repr__(self):
      return "File('%s')" % self.filename


    def make_path(self, directory=None):
        """Wraps this files' filename so that a complete path is formed

        Keyword parameters:

        directory
          An optional directory name that will be prefixed to the returned result.

        Returns a string containing the newly generated file path.
        """

        if not directory:
            directory = ''

        return os.path.join(directory, self.filename)


    def is_mirrored(self):
        return self.mirrored


    def get_client_id(self):
        return self.client_id


    def load(self, directory=None):
        """Loads the data at the specified location.

        Keyword parameters:

        directory
          [optional] If not empty or None, this directory is prefixed to the final
          file destination
        """
        data = bob.io.base.load(self.make_path(directory))

        if self.mirrored:
            return data[:,:,::-1].copy()

        return data
