#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x424264c8

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

import tensorflow as tf

from abc import ABCMeta
from abc import abstractmethod
from .interfaces.model_base import BaseInterface
from .utils import Required
from .utils import TENSOR


class ModelBase(BaseInterface):
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        self.global_step = -1

        initialize_variables = kwargs.pop("initialize_variables", True)
        restore = kwargs.pop("restore", False)
        self.model_path = kwargs.pop("model_path", "model")
        self.logs_path = kwargs.pop("logs_path", "logs")
        flush_secs = kwargs.pop("flush_secs", 10.0)
        self.graph = kwargs.pop("graph", tf.Graph())

        self.sess = tf.Session(graph=self.graph)
        self.define_model(*args, **kwargs)

        if not hasattr(self, 'global_step'):
            self.global_step = 0

        with self.graph.as_default() :
            self.set_summaries()
            self.writer = tf.summary.FileWriter(self.logs_path, graph=self.graph, flush_secs=flush_secs)
            self.saver = tf.train.Saver(allow_empty=True)

            if not initialize_variables:
                return
            elif restore:
                self.saver.restore(self.sess, self.model_path)
            else:
                self.initialize_variables()



    @abstractmethod
    def define_model(self, *args, **kwargs):
        pass

    def initialize_variables(self):
        self.sess.run(tf.global_variables_initializer())

    def save(self, model_path=None):
        model_path = self.model_path if not model_path else model_path
        self.saver.save(self.sess, model_path)

    def restore(self, model_path=None):
        model_path = self.model_path if not model_path else model_path

        self.sess.close()
        self.sess = tf.Session(graph=self.graph)
        self.saver.restore(self.sess, model_path)

    def set_summaries(self):
        with self.graph.as_default() :
            if self.summaries is TENSOR:  #not set
                self.summaries = tf.summary.merge_all()

            if self.summaries is None:
                self.summaries = tf.no_op()
