##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Stats implementations
"""

import abc
import six

@six.add_metaclass(abc.ABCMeta)
class AbstractStats(object):

    def __init__(self, connmanager):
        self.connmanager = connmanager

    def get_object_count(self):
        """Returns the number of objects in the database"""
        # do later
        return 0

    @abc.abstractmethod
    def get_db_size(self):
        """Returns the approximate size of the database in bytes"""
        raise NotImplementedError()
