#!/usr/bin/env python
"""ieval.py: interactive evaluation"""
__author__ = "Fabien Cromieres"
__license__ = "undecided"
__version__ = "1.0"
__email__ = "fabien.cromieres@gmail.com"
__status__ = "Development"

import json
import numpy as np
from chainer import cuda, serializers

import models
from make_data import Indexer, build_dataset_one_side
# from utils import make_batch_src, make_batch_src_tgt, minibatch_provider, compute_bleu_with_unk_as_wrong, de_batch
from evaluation import (greedy_batch_translate, 
                        convert_idx_to_string, 
                        batch_align, 
                        beam_search_translate, 
                        convert_idx_to_string_with_attn)

import visualisation

import logging
import codecs
import sys
# import h5py

from pyknp import Juman

logging.basicConfig()
log = logging.getLogger("rnns:eval")
log.setLevel(logging.INFO)

def commandline():
    
    import argparse
    parser = argparse.ArgumentParser(description= "Use a RNNSearch model", 
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("training_config", help = "prefix of the trained model")
    parser.add_argument("trained_model", help = "prefix of the trained model")
    parser.add_argument("--gpu", type = int, help = "specify gpu number to use, if any")
    
    parser.add_argument("--beam_width", type = int, default= 20, help = "beam width")
    parser.add_argument("--nb_steps", type = int, default= 50, help = "nb_steps used in generation")
    parser.add_argument("--nb_steps_ratio", type = float, help = "nb_steps used in generation as a ratio of input length")
    parser.add_argument("--beam_opt", default = False, action = "store_true")
    
    parser.add_argument("--juman_port", type = int, help = "juman server port")
    
    args = parser.parse_args()
    
    config_training_fn = args.training_config #args.model_prefix + ".train.config"
    
    log.info("loading model config from %s" % config_training_fn)
    config_training = json.load(open(config_training_fn))

    voc_fn = config_training["voc"]
    log.info("loading voc from %s"% voc_fn)
    src_voc, tgt_voc = json.load(open(voc_fn))
    
    src_indexer = Indexer.make_from_serializable(src_voc)
    tgt_indexer = Indexer.make_from_serializable(tgt_voc)
    tgt_voc = None
    src_voc = None
    
#     Vi = len(src_voc) + 1 # + UNK
#     Vo = len(tgt_voc) + 1 # + UNK
    
    Vi = len(src_indexer) # + UNK
    Vo = len(tgt_indexer) # + UNK
    
    print config_training
    
    Ei = config_training["command_line"]["Ei"]
    Hi = config_training["command_line"]["Hi"]
    Eo = config_training["command_line"]["Eo"]
    Ho = config_training["command_line"]["Ho"]
    Ha = config_training["command_line"]["Ha"]
    Hl = config_training["command_line"]["Hl"]
    
    eos_idx = Vo
    encdec = models.EncoderDecoder(Vi, Ei, Hi, Vo + 1, Eo, Ho, Ha, Hl)
    
    log.info("loading model from %s" % args.trained_model)
    serializers.load_npz(args.trained_model, encdec)
    
    if args.gpu is not None:
        encdec = encdec.to_gpu(args.gpu)
        
        
    
    juman = None
    if args.juman_port is not None:
        juman = Juman(server='localhost', port=args.juman_port)
    
    
    for line in codecs.getreader('utf_8')(sys.stdin):
        line = line.strip()
        if juman is not None:
            analysed = juman.analysis(line)
            splitted = [mrph.midasi for mrph in analysed.mrph_list()]
        else:
            splitted =  line.split(" ")
        print "splitted:", " || ".join(splitted)
        seq_src, unk_cnt_src= src_indexer.convert_with_unk_count(splitted)
        out = codecs.getwriter('utf_8')(sys.stdout) #sys.stdout #codecs.open(args.dest_fn, "w", encoding = "utf8")
        with cuda.cupy.cuda.Device(args.gpu):
            translations_gen = beam_search_translate(
                        encdec, eos_idx, [seq_src], beam_width = args.beam_width, nb_steps = args.nb_steps, 
                                                 gpu = args.gpu, beam_opt = args.beam_opt, nb_steps_ratio = args.nb_steps_ratio,
                                                 need_attention = True)
            
            for t, score, attn in translations_gen:
                ct = convert_idx_to_string_with_attn(t, tgt_voc, attn, unk_idx = len(tgt_voc))
                out.write(ct + "\n")

if __name__ == '__main__':
    commandline() 
    
    