# This file is part of the pyMOR project (http://www.pymor.org).
# Copyright 2013-2016 pyMOR developers and contributors. All rights reserved.
# License: BSD 2-Clause License (http://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function

from pymor.core.interfaces import BasicInterface


class RemoteObjectManager(BasicInterface):
    """A simple context manager to keep track of |RemoteObjects|.

    When leaving this context, all |RemoteObjects| that have been
    :meth:`managed <manage>` by this object will be
    :meth:`removed <pymor.parallel.interfaces.RemoteObjectInterface.remove>`.
    """

    def __init__(self):
        self.remote_objects = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.remove_objects()

    def __del__(self):
        self.remove_objects()

    def remove_objects(self):
        """Call :meth:`~pymor.parallel.interfaces.RemoteObjectInterface.remove` for all managed objects."""
        for obj in self.remote_objects:
            obj.remove()
        del self.remote_objects[:]

    def manage(self, remote_object):
        """Add a |RemoteObject| to the list of managed objects.

        Parameters
        ----------
        remote_object
            The object to add to the list.

        Returns
        -------
        `remote_object`
        """
        self.remote_objects.append(remote_object)
        return remote_object
