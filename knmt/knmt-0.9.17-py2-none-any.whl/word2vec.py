import numpy as np
import chainer
from chainer import cuda, Function, gradient_check, Variable, optimizers, serializers, utils
from chainer import Link, Chain, ChainList
import chainer.functions as F
import chainer.links as L

import codecs
import logging
import sys
from collections import defaultdict
from operator import itemgetter
import json
from itertools import islice

logging.basicConfig()
log = logging.getLogger("w2v")
log.setLevel(logging.INFO)

class W2V(Chain):
    def __init__(self, V, E, verbose = False):
        super(W2V, self).__init__(
            emb = L.EmbedID(V, E),
            lin_o = L.Linear(E, V),
        )
        
        self.E = E
        self.V = V
        
        if verbose:
            log.info("created W2V model with V:%i E:%i"%(V, E))
        
    def loss(self, inputs, targets):
        mb_size = inputs.data.shape[0]
        
        embedded = self.emb(inputs)
        h = F.sum(embedded, axis = 1)
        assert h.data.shape == (mb_size, self.E)
        
        o = self.lin_o(h)
        
        return F.softmax_cross_entropy(o, targets)

def shuffle_in_unison(a, b):
    assert len(a) == len(b)
    p = np.random.permutation(len(a))
    return a[p], b[p]

EOS_tag = "$#EOS#!"
BOS_tag = "$#BOS#!"

def make_data(filename, ctxt_size, max_nb_lines = None):
    count = defaultdict(int)
    nb_elems = 0
    
    log.info("building indexer")
    with codecs.open(filename, encoding = "utf8") as f:
        for line in islice(f, max_nb_lines):
            count[EOS_tag] += 1
            count[BOS_tag] += 1
            for word in line.strip().split(" "):
                count[word] += 1
                nb_elems += 1
    
    log.info("done building indexer types (inc. EOS/BOS): %i tokens (not inc. EOS/BOS): %i"%(len(count), nb_elems))
    
    word_by_freq = count.items()
    word_by_freq.sort(key = itemgetter(1), reverse = True)
    
    indexer = dict((w, idx) for idx, (w, c) in enumerate(word_by_freq))
    bos_idx = indexer[BOS_tag]
    eos_idx = indexer[EOS_tag]
    
    inputs = np.empty((nb_elems, ctxt_size * 2), dtype = np.int32)
    targets = np.empty((nb_elems,), dtype = np.int32)
    
    log.info("building data")
    with codecs.open(filename, encoding = "utf8") as f:
        num_elem = 0
        for line in islice(f, max_nb_lines):
            splitted = line.strip().split(" ")
            for i in xrange(len(splitted)):
                wi = splitted[i]
                wi_idx = indexer[wi]
                targets[num_elem] = wi_idx
                for j in xrange(ctxt_size *2):
                    offset = (j/2 + 1) * ( (-1)^(j%2) ) 
                    ctxt_i = i + offset
                    if ctxt_i < 0:
                        ctxt_idx = bos_idx
                    elif ctxt_i >= len(splitted):
                        ctxt_idx = eos_idx
                    else:
                        ctxt_idx = indexer[splitted[ctxt_i]]
                    inputs[num_elem, j] = ctxt_idx
                num_elem += 1
                
        assert num_elem == nb_elems
    log.info("done building data") 
            
    return {"word_by_freq": word_by_freq, "indexer": indexer}, inputs, targets
    

def train(model, inputs, targets, gpu, model_fn):
    log.info("shuffling data")
    inputs, targets = shuffle_in_unison(inputs, targets)
    log.info("done shuffling data")
    
    def mb_provider(mb_size):
        cursor = 0
        while 1:
            mb_i = inputs[cursor: cursor + mb_size]
            mb_t = targets[cursor: cursor + mb_size]
            
            if gpu is not None:
                mb_i = cuda.to_gpu(mb_i, gpu)
                mb_t = cuda.to_gpu(mb_t, gpu)
            yield Variable(mb_i), Variable(mb_t)
            cursor += mb_size
            if cursor >= len(inputs):
                log.info("finished one epoch")
                cursor = 0
        
    mbp = mb_provider(256)
        
    optimizer = optimizers.Adam()
    optimizer.setup(model)
    
    def train_once(verbose = False):
        inp, tgt = mbp.next()
        model.zerograds()
        loss = model.loss(inp, tgt)
        if verbose:
            log.info("loss: %f"%loss.data)
        loss.backward()
        optimizer.update()
        
    try:
        for num_iter in xrange(sys.maxint):
            if num_iter % 100 == 0:
                print num_iter
            train_once(num_iter % 100 == 0)
    finally:
        serializers.save_npz(model_fn, model)
        
        
def commandline():
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--filename")
    parser.add_argument("--output_prefix")
    parser.add_argument("--data_prefix")
    parser.add_argument("--mode", choices = ["train", "make"], default = "train")
    
    parser.add_argument("--max_nb_lines", type = int)
    parser.add_argument("--ctxt_size", type = int, default = 2)
    parser.add_argument("--embedding_size", type = int, default = 200)
    
    parser.add_argument("--gpu", type = int)
    args = parser.parse_args()
    
    if args.mode == "make":
        log.info("creating data")
        voc_info, inputs, targets = make_data(args.filename, args.ctxt_size, max_nb_lines = args.max_nb_lines)
        
        log.info("saving data")
        np.savez(args.output_prefix + ".data.npz", inputs = inputs, targets = targets)
        json.dump(voc_info, open(args.output_prefix + ".voc_info.json", "w"))
        
    else:
        log.info("training mode")
        data = np.load(args.data_prefix + ".data.npz")
        inputs = data["inputs"]
        targets = data["targets"]
        
        voc_info = json.load(open(args.data_prefix + ".voc_info.json"))
        V = len(voc_info["word_by_freq"])
        
        model = W2V(V, args.embedding_size, verbose = True)
        
        with cuda.get_device(args.gpu):
            
            if args.gpu is not None:
                model = model.to_gpu(args.gpu)
            log.info("data loaded")
           
            
            train(model, inputs, targets, args.gpu, args.output_prefix + ".model.npz")
        
    
if __name__ == '__main__':
    commandline()
        
        