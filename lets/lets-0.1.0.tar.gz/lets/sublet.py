# -*- coding: utf-8 -*-
"""
   lets.sublet
   ~~~~~~~~~~~

   :copyright: (c) 2013-2017 by Heungsub Lee
   :license: BSD, see LICENSE for more details.

"""
from __future__ import absolute_import


__all__ = ['Sublet']


class Sublet(gevent.Greenlet):
