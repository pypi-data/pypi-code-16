#!/usr/bin/env python
"""legacy_models.py: For backward compatibility"""
__author__ = "Fabien Cromieres"
__license__ = "undecided"
__version__ = "1.0"
__email__ = "fabien.cromieres@gmail.com"
__status__ = "Development"

from _collections import defaultdict
import numpy as np
import chainer
from chainer import cuda, Variable
from chainer import Link, Chain, ChainList
import chainer.functions as F
import chainer.links as L
import math, random

import rnn_cells
from utils import ortho_init

import logging
logging.basicConfig()
log = logging.getLogger("rnns:legacy_models")
log.setLevel(logging.INFO)

class Encoder(Chain):
    """ Chain that encode a sequence. 
        The __call_ takes 2 parameters: sequence and mask.
        mask and length should be 2 python lists of same length #length.
        
        sequence should be a python list of Chainer Variables wrapping a numpy/cupy array of shape (mb_size,) and type int32 each.
            -- where mb_size is the minibatch size
        sequence[i].data[j] should be the jth element of source sequence number i, or a padding value if the sequence number i is
            shorter than j.
        
        mask should be a python list of Chainer Variables wrapping a numpy/cupy array of shape (mb_size,) and type bool each.
        mask[i].data[j] should be True if and only if sequence[i].data[j] is not a padding value.
        
        Return a chainer variable of shape (mb_size, #length, 2*Hi) and type float32
    """
    def __init__(self, Vi, Ei, Hi, init_orth = False, use_bn_length = 0, cell_type = rnn_cells.LSTMCell):
        assert cell_type in "gru dgru lstm slow_gru".split()
        self.cell_type = cell_type
        if cell_type == "gru":
            gru_f = faster_gru.GRU(Hi, Ei)
            gru_b = faster_gru.GRU(Hi, Ei)
        elif cell_type == "dgru":
            gru_f = DoubleGRU(Hi, Ei)
            gru_b = DoubleGRU(Hi, Ei)
        elif cell_type == "lstm":
            gru_f = L.StatelessLSTM(Ei, Hi) #, forget_bias_init = 3)
            gru_b = L.StatelessLSTM(Ei, Hi) #, forget_bias_init = 3)
        if cell_type == "slow_gru":
            gru_f = L.GRU(Hi, Ei)
            gru_b = L.GRU(Hi, Ei)
#             
        gru_f = cell_type(Ei, Hi)
        gru_b = cell_type(Ei, Hi)
                  
        log.info("constructing encoder [%s]"%(cell_type,))
        super(Encoder, self).__init__(
            emb = L.EmbedID(Vi, Ei),
#             gru_f = L.GRU(Hi, Ei),
#             gru_b = L.GRU(Hi, Ei)
            
            gru_f = gru_f,
            gru_b = gru_b
        )
        self.Hi = Hi
#         self.add_param("initial_state_f", (1, Hi))
#         self.add_param("initial_state_b", (1, Hi))
# 
#         self.initial_state_f.data[...] = np.random.randn(Hi)
#         self.initial_state_b.data[...] = np.random.randn(Hi)
#         
#         if cell_type == "lstm":
#             self.add_persistent("initial_cell_f", self.xp.zeros((1, self.Hi), dtype = self.xp.float32))
#             self.add_persistent("initial_cell_b", self.xp.zeros((1, self.Hi), dtype = self.xp.float32))
            
#             self.initial_cell_f = self.xp.zeros((1, self.Hi), dtype = self.xp.float32)
#             self.initial_cell_b = self.xp.zeros((1, self.Hi), dtype = self.xp.float32)  
        
        if use_bn_length > 0:
            self.add_link("bn_f", BNList(Hi, use_bn_length))
#             self.add_link("bn_b", BNList(Hi, use_bn_length)) #TODO
        self.use_bn_length = use_bn_length
        
        if init_orth:
            ortho_init(self.gru_f)
            ortho_init(self.gru_b)
        
