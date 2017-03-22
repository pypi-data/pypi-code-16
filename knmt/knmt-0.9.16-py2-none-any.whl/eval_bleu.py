#!/usr/bin/env python
"""eval_bleu.py: evaluate bleu score"""
__author__ = "Fabien Cromieres"
__license__ = "undecided"
__version__ = "1.0"
__email__ = "fabien.cromieres@gmail.com"
__status__ = "Development"

import json
import numpy as np
from chainer import cuda, serializers
import sys
import models
from make_data import Indexer, build_dataset_one_side
# from utils import make_batch_src, make_batch_src_tgt, minibatch_provider, compute_bleu_with_unk_as_wrong, de_batch
from evaluation import (greedy_batch_translate, 
#                         convert_idx_to_string, 
                        batch_align, 
                        beam_search_translate, 
#                         convert_idx_to_string_with_attn
                        )

import visualisation

import logging
import codecs
# import h5py

logging.basicConfig()
log = logging.getLogger("rnns:eval")
log.setLevel(logging.INFO)


def commandline():
    
    import argparse
    parser = argparse.ArgumentParser(description= "Use a RNNSearch model", 
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("training_config", help = "prefix of the trained model")
    parser.add_argument("trained_model", help = "prefix of the trained model")
    parser.add_argument("src_fn", help = "source text")
    parser.add_argument("dest_fn", help = "destination file")
    parser.add_argument("ref", help = "destination file")
    
    
    parser.add_argument("--tgt_fn", help = "target text")
    parser.add_argument("--mode", default = "translate", 
                        choices = ["translate", "align", "translate_attn", "beam_search", "eval_bleu"], help = "target text")
    
    parser.add_argument("--ref", help = "target text")
    
    parser.add_argument("--gpu", type = int, help = "specify gpu number to use, if any")
    
    parser.add_argument("--max_nb_ex", type = int, help = "only use the first MAX_NB_EX examples")
    parser.add_argument("--mb_size", type = int, default= 80, help = "Minibatch size")
    parser.add_argument("--beam_width", type = int, default= 20, help = "beam width")
    parser.add_argument("--nb_steps", type = int, default= 50, help = "nb_steps used in generation")
    parser.add_argument("--nb_steps_ratio", type = float, help = "nb_steps used in generation as a ratio of input length")
    parser.add_argument("--nb_batch_to_sort", type = int, default= 20, help = "Sort this many batches by size.")
    parser.add_argument("--beam_opt", default = False, action = "store_true")
    parser.add_argument("--tgt_unk_id", choices = ["attn", "id"], default = "align")
    parser.add_argument("--groundhog", default = False, action = "store_true")
    
    parser.add_argument("--use_raw_score", default = False, action = "store_true")
    
    args = parser.parse_args()
    
    import subprocess
    subprocess.check_call("python ")
    
    
    