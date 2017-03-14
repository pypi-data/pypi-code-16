#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x8cb1a4d6

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

from .supervised_model import SupervisedModel
import tensorflow as tf
from tensorflow import layers

class LinearRegression(SupervisedModel):

    def define_model(self, learning_rate=0.01):
        with self.graph.as_default() :
            self.x = tf.placeholder(tf.float32, [None, 1])
            self.y = tf.placeholder(tf.float32, [None, 1])

            self.h = (_coconut_partial(layers.dense, {1: 1}, 2))(self.x)

            error = self.h - self.y

            self.loss = ((tf.reduce_mean)((tf.nn.l2_loss)(error)))

            tf.summary.scalar('loss', self.loss)

            trainer = tf.train.AdamOptimizer(learning_rate)
            self.update = trainer.minimize(self.loss)
