#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x693642c4

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

class Required(object):
    pass
class RequiredTensor(Required):
    pass
class RequiredEnvironment(Required):
    pass
class RequiredModel(Required):
    pass
class RequiredExperienceBuffer(Required):
    pass
class RequiredTrainer(Required):
    pass

REQUIRED = Required()
TENSOR = RequiredTensor()
MODEL = RequiredModel()
ENV = RequiredEnvironment()
EXPERIENCEBUFFER = RequiredExperienceBuffer()
TRAINER = RequiredTrainer()


@_coconut_tco
def select_columns(tensor, indexes):
    idx = tf.stack((tf.range(tf.shape(indexes)[0]), indexes), 1)
    raise _coconut_tail_call(tf.gather_nd, tensor, idx)


def soft_if(cond, then, else_):
    return (cond * then) + (1.0 - cond) * else_


def map_gradients(gradients, f):
    return [(f(g), v) for g, v in gradients]

def get_run():
    try:
        with open("run.txt") as f :
            run = int(f.read().split("/n")[0])
    except:
        run = -1

    with open("run.txt", 'w+') as f :
        run += 1

        f.seek(0)
        f.write(str(run))
        f.truncate()

    return run
