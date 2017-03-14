#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xcb395bd0

# Compiled with Coconut version 1.2.2-post_dev5 [Colonel]

# Coconut Header: --------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

import sys as _coconut_sys, os.path as _coconut_os_path
_coconut_file_path = _coconut_os_path.dirname(_coconut_os_path.abspath(__file__))
_coconut_sys.path.insert(0, _coconut_file_path)
from __coconut__ import _coconut, _coconut_MatchError, _coconut_tail_call, _coconut_tco, _coconut_igetitem, _coconut_compose, _coconut_pipe, _coconut_starpipe, _coconut_backpipe, _coconut_backstarpipe, _coconut_bool_and, _coconut_bool_or, _coconut_minus, _coconut_tee, _coconut_map, _coconut_partial
from __coconut__ import *
_coconut_sys.path.remove(_coconut_file_path)

# Compiled Coconut: ------------------------------------------------------

from abc import ABCMeta
from abc import abstractmethod
import random

class ExperienceBufferInterface(object):
    """docstring for ExperienceBufferInterface."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def append(self, experience):
        pass

    @abstractmethod
    def random_batch(self, batch_size):
        pass

    @abstractmethod
    def unzip(self):
        pass

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def __getitem__(self):
        pass

    @_coconut_tco
    def get_random_idx(self, batch_size):
        n = len(self)
        batch_size = min(batch_size, n)
        idx = range(n)
        raise _coconut_tail_call(random.sample, idx, batch_size)
