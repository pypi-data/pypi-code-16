import codecs, json, random, gzip

import numpy as np
import chainer
from chainer import cuda, Function, gradient_check, Variable, optimizers, serializers, utils
from chainer import Link, Chain, ChainList
import chainer.functions as F
import chainer.links as L

import logging
from chainer.testing.attr import gpu

logging.basicConfig()
log = logging.getLogger("vtc:clm")
log.setLevel(logging.INFO)


class CharEncoderDecoder(Chain):
    def __init__(self, Hw, Hc, Vc):
        super(CharEncoderDecoder, self).__init__(
#             bil = L.Bilinear(Hi, Hs, Hs),
            lstm = L.GRU(Hw, Hc),
            lin_o = L.Linear(Hw, Vc + 1),
            emb_c = L.EmbedID(Vc + 1, Hc)
        )
        self.eos_idx = Vc
        
        self.Hw = Hw
        self.Hc = Hc
        self.Vc = Vc
        
        self.add_param("initial_state_encoder", (1, Hw))
        self.initial_state_encoder.data[...] = np.random.randn(Hw)
        
    def get_eos_idx(self):
        return self.eos_idx
         
#     def xp(self):
#         return cuda.get_array_module(self.initial_state_encoder.data)
    
    def get_initial_state(self, mb_size):
        initial_state = F.broadcast_to(
                            self.initial_state_encoder, 
                            (mb_size, self.Hw) 
                            )
        return initial_state
         
    def encode_one(self, seq):
        seq_length = len(seq)
        mb_size = seq[0].data.shape[0]
        assert mb_size == 1
        current_state = self.get_initial_state(mb_size)
        for i in xrange(seq_length):
            next_char = seq[i]
            embedded_char = self.emb_c(next_char)
            current_state = self.lstm(current_state, embedded_char)
        return current_state
    
    def encode_batch(self, seq, mask):
        seq_length = len(seq)
        mb_size = seq[0].data.shape[0]
        current_state = self.get_initial_state(mb_size)
        for i in xrange(seq_length):
            next_char = seq[i]
            embedded_char = self.emb_c(next_char)
            current_state = F.where(F.broadcast_to(F.reshape(mask[i], (mb_size, 1)), (mb_size, self.Hw)), self.lstm(current_state, embedded_char), current_state)
        return current_state
        
    def decode_loss_one(self, encoded, target):
        seq_length = len(target)
        mb_size = target[0].data.shape[0]
        assert mb_size == 1
        
        current_state = encoded
        
        loss = 0
        for i in xrange(seq_length):
            logits = self.lin_o(current_state)
            next_char = target[i]
            current_loss = F.softmax_cross_entropy(logits, next_char)
            loss += current_loss
            embedded_char = self.emb_c(next_char)
            current_state = self.lstm(current_state, embedded_char)
        return loss    
       
    def decode_loss_batch(self, encoded, target):
        seq_length = len(target)
        mb_size = target[0].data.shape[0]
        
        current_state = encoded
        
        loss = 0
        for i in xrange(seq_length):
            logits = self.lin_o(current_state)
            next_char = target[i]
            current_loss = F.softmax_cross_entropy(logits, next_char)
            loss += current_loss
            embedded_char = self.emb_c(next_char)
            current_state = self.lstm(current_state, embedded_char)
        return loss
    
    def decode_loss_batch_and_backward(self, encoded, target):
        loss =self.decode_loss_batch(encoded, target)
        loss.backward()
        return loss.data  
        
    def decode_search_one(self, encoded, max_len):
#         xp = self.xp()
        mb_size = encoded.data.shape[0]
        assert mb_size == 1
        current_state = encoded
        seqs = []
        for i in xrange(max_len):
            logits = self.lin_o(current_state)
            next_char = self.xp.argmax(logits.data, axis = 1)
            seqs.append(int(next_char))
            if seqs[-1] == self.eos_idx:
                break
            embedded_char = self.emb_c(Variable(next_char.astype(self.xp.int32), volatile = "auto"))
            current_state = self.lstm(current_state, embedded_char)
        return seqs
            
    def decode_search_batch(self, encoded, max_len):
#         xp = self.xp()
        mb_size = encoded.data.shape[0]
        current_state = encoded
        seqs = []
        for i in xrange(max_len):
            logits = self.lin_o(current_state)
            next_char = self.xp.argmax(logits.data, axis = 1)
            seqs.append(int(next_char))
            if seqs[-1] == self.eos_idx:
                break
            embedded_char = self.emb_c(Variable(next_char.astype(self.xp.int32), volatile = "auto"))
            current_state = self.lstm(current_state, embedded_char)
        return seqs

class LMWithCED(Chain):
    def __init__(self, Hw, Hc, Vc, Hs):
        super(LMWithCED, self).__init__(
            lstm = L.GRU(Hs, Hw),
            ced = CharEncoderDecoder(Hw, Hc, Vc + 1),
            lin_o = L.Linear(Hs, Hw)
        )
        self.Hc = Hc
        self.Hw = Hw
        self.Vc = Vc
        self.Hs = Hs
        self.add_param("initial_state", (1, Hs))
        self.initial_state.data[...] = np.random.randn(Hs)
        
        self.eos = Vc
        
    def get_eos(self):
        return self.eos
    
    def get_eow(self):
        return self.ced.get_eos_idx()
        
    def get_initial_state(self, mb_size):
        initial_state = F.broadcast_to(
                            self.initial_state, 
                            (mb_size, self.Hs) 
                            )
        return initial_state
        
    def compute_loss(self, tgts):
        mb_size = tgts[0][0][0].data.shape[0]
        current_state = self.get_initial_state(mb_size)
        loss = 0
        for i in xrange(len(tgts) - 1):
            w_i, mask_i = tgts[i]
            encoded_w_out = F.tanh(self.lin_o(current_state))
            current_loss = self.ced.decode_loss_batch(encoded_w_out, w_i)
            loss += current_loss
            encoded_w_in = self.ced.encode_batch(w_i, mask_i)
#             print encoded_w.data.shape
#             print current_state.data.shape
            current_state = self.lstm(current_state, encoded_w_in)
        return loss

    def sample(self, nb_steps, nb_steps_w):
        current_state = self.get_initial_state(1)
        seq = []
        for i in xrange(nb_steps):
            encoded_w_out = F.tanh(self.lin_o(current_state))
            w = self.ced.decode_search_one(encoded_w_out, nb_steps_w)
            seq.append(w)
#             print w
            if seq[-1][0] == self.eos:
                break
            encoded_w = self.ced.encode_one(
                [Variable(self.xp.array([c], dtype = self.xp.int32), volatile = "auto") for c in w])
            current_state = self.lstm(current_state, encoded_w)
        return seq
    
def make_batch_char(seqs, eow_idx, eos_idx, gpu = None):
    max_len = max((len(s) if  s is not None else 1) for s in seqs if (s != -1)) + 1
    targets = []
    masks = []
    for i in xrange(max_len):
        cur_var = []
        cur_mask = []
        for j in xrange(len(seqs)):
            if seqs[j] == -1:
                cur_var.append(-1)
                cur_mask.append(False)
            elif seqs[j] is None:
                if i == 0:
                    cur_var.append(eos_idx)
                    cur_mask.append(True)
                else:
                    cur_var.append(-1)
                    cur_mask.append(False)                    
            elif i < len(seqs[j]):
                cur_var.append(seqs[j][i])
                cur_mask.append(True)
            elif i == len(seqs[j]):
                cur_var.append(eow_idx)
                cur_mask.append(True)
            else:
                cur_var.append(-1)
                cur_mask.append(False)
#         print cur_var
        seq_i = np.array(cur_var, dtype = np.int32)
        mask_i = np.array(cur_mask, dtype = np.bool)
        if gpu is not None:
            seq_i = cuda.to_gpu(seq_i, gpu)
            mask_i = cuda.to_gpu(mask_i, gpu)
        targets.append(Variable(seq_i))
        masks.append(Variable(mask_i))
    return targets, masks

def make_batch_sentence_level(seqs):
    max_len = max(len(s) for s in seqs) + 1
    targets = []
    masks = []
    for i in xrange(max_len):
        cur_var = []
        cur_mask = []
        for j in xrange(len(seqs)):
            if i < len(seqs[j]):
                cur_var.append(seqs[j][i])
                cur_mask.append(True)
            elif i == len(seqs[j]):
                cur_var.append(None)
                cur_mask.append(True)
            else:
                cur_var.append(-1)
                cur_mask.append(False)
        targets.append(cur_var)
        masks.append(cur_mask)
    return targets, masks

def make_full_batch(inpts, eow, eos, gpu = None):
    bs, bm = make_batch_sentence_level(inpts)
#     print bs
    
    full_b = []
    for i in xrange(len(bs)):
        full_b.append(make_batch_char(bs[i], eow, eos, gpu = gpu))
    return full_b, bm
#     for i in xrange(len(full_b)):
#         v1, mask = full_b[i]
#         print i
#         for vc in v1:
#             print vc.data

def commandline():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("data_prefix")
    parser.add_argument("save_prefix")
    parser.add_argument("--mb_size", type = int, default = 64)
    parser.add_argument("--max_nb_ex", type = int)
    parser.add_argument("--gpu")
    parser.add_argument("--load_model")
    args = parser.parse_args()
    
    log.info("loading")
    datas = json.load(gzip.open(args.data_prefix + ".data.json.gzip"))
    voc = json.load(open(args.data_prefix + ".voc.json"))
    log.info("loaded")
    
    datas = datas[:args.max_nb_ex]
    
    from utils import minibatch_looper, batch_sort_and_split
    
    
    
    def sorted_minibatch_provider(mb_size, nb_to_sort):
        mb_looper = minibatch_looper(datas, mb_size = mb_size * nb_to_sort, 
                     loop = True, avoid_copy = False)
        
        for batch in mb_looper:
            for sorted_mb in batch_sort_and_split(batch, mb_size, sort_key = lambda x:len(x), inplace = True):
                yield sorted_mb
    
    Vc = len(voc)
#     Hw, Hc, Hs = 200, 50, 500
    
    Hw, Hc, Hs = 200, 50, 1000
    
    log.info("creating nn")
    edec = LMWithCED(Hw, Hc, Vc, Hs)
    
    if args.load_model:
        serializers.load_npz(args.load_model, edec)
    
    if args.gpu is not None:
        edec = edec.to_gpu(args.gpu)
    log.info("created")
    
    mb_looper = sorted_minibatch_provider(args.mb_size, 20)

    
    adaoptim = optimizers.AdaDelta()
    adaoptim.setup(edec)
    
    adaoptim.add_hook(chainer.optimizer.GradientClipping(1))
    
    def train_once():
        seqs = mb_looper.next()
        tgts, global_mask = make_full_batch(seqs, edec.get_eow(), edec.get_eos(), gpu = args.gpu)
        edec.zerograds()
        loss = edec.compute_loss(tgts)
        print loss.data
        loss.backward()
        adaoptim.update()        
        
    num_iter = 0
    
    voc_plus = voc + ["#EOS#", "$$$"]
    try:
        while 1:
            print num_iter,
            train_once()
            if num_iter % 25 == 0:
                
                seq = edec.sample(70, 30)
                print seq
                for w in seq:
                    print "".join([voc_plus[c] for c in w]),
                print
            num_iter += 1
    finally:
        fn_save = args.save_prefix + ".model.npz"
        log.info("saving model to %s" % fn_save)
        serializers.save_npz(fn_save, edec)
    
    
if __name__ == '__main__':
    commandline()


