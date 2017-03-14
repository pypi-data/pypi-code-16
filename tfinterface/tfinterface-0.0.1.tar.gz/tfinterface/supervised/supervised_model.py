#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xc01978fa

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

from abc import abstractmethod
import random
import tensorflow as tf

from tfinterface.model_base import ModelBase
from tfinterface.interfaces import SupervisedInterface
from tfinterface.interfaces import TrainerInterface
from tfinterface.utils import TENSOR

class SupervisedModel(ModelBase, SupervisedInterface):

    @_coconut_tco
    def predict(self, X, **kwargs):
        feed_dict = self.predict_feed(X, **kwargs)
        raise _coconut_tail_call(self.sess.run, self.h, feed_dict=feed_dict)

    def fit_feed(self, x, y, **kwargs):
        return {self.x: x, self.y: y}

    def predict_feed(self, x, **kwargs):
        return {self.x: x}

    def fit(self, *args, **kwargs):
        self.trainer.fit(*args, **kwargs)

    @property
    def default_trainer(self):
        return SupervisedTrainer


class SupervisedTrainer(TrainerInterface):
    """docstring for SupervisedTrainer."""
    def __init__(self, model):
        super(SupervisedTrainer, self).__init__()
        self.model = model


    def fit(self, *args, **kwargs):
        batch_size = kwargs.get('batch_size', 64)
        learning_rate = kwargs.get('learning_rate', 0.01)
        epochs = kwargs.get('epochs', 2000)

        model = self.model

        for i in range(epochs):
            [_, summaries] = model.sess.run([model.update, model.summaries], feed_dict=self.feed_fn(batch_size, args, kwargs))

            if isinstance(model.global_step, (tf.Tensor, tf.Variable)):
                global_step = model.sess.run(model.global_step)
            else:
                model.global_step += 1
                global_step = model.global_step

            if summaries is not None:
                model.writer.add_summary(summaries, global_step=global_step)

    @_coconut_tco
    def feed_fn(self, batch_size, args, kwargs):
        if batch_size is not None:
            vars = self.random_batch(*args, **kwargs)
            raise _coconut_tail_call(self.model.fit_feed, *args, **kwargs)
        else:
            return {}

    @_coconut_tco
    def random_batch(self, *vars, **kwargs):
        total_length = len(vars[0])
        batch_size = kwargs.get('batch_size', min(64, total_length))

        idxs = random.sample(range(total_length), batch_size)
        raise _coconut_tail_call(tuple, [var[idxs] for var in vars])
