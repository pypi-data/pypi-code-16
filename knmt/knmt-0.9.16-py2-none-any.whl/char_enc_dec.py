import codecs, json, random

import numpy as np
import chainer
from chainer import cuda, Function, gradient_check, Variable, optimizers, serializers, utils
from chainer import Link, Chain, ChainList
import chainer.functions as F
import chainer.links as L

import logging
from chainer.testing.attr import gpu

logging.basicConfig()
log = logging.getLogger("vtc:edec")
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
         
def make_batch(seqs, eos_idx, gpu = None):
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
                cur_var.append(eos_idx)
                cur_mask.append(True)
            else:
                cur_var.append(-1)
                cur_mask.append(False)
                
        seq_i = np.array(cur_var, dtype = np.int32)
        mask_i = np.array(cur_mask, dtype = np.bool)
        if gpu is not None:
            seq_i = cuda.to_gpu(seq_i, gpu)
            mask_i = cuda.to_gpu(mask_i, gpu)
        targets.append(Variable(seq_i))
        masks.append(Variable(mask_i))
    return targets, masks

def commandline():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("data_prefix")
    parser.add_argument("save_prefix")
    parser.add_argument("--gpu")
    parser.add_argument("--load_model")
    parser.add_argument("--mb_size", type = int, default = 256)
    parser.add_argument("--optimizer", choices=["sgd", "rmsprop", "rmspropgraves", 
                            "momentum", "nesterov", "adam", "adagrad", "adadelta"], 
                        default = "adadelta")
    parser.add_argument("--learning_rate", type = float, default= 0.01, help = "Learning Rate")
    parser.add_argument("--momentum", type = float, default= 0.9, help = "Momentum term")
    args = parser.parse_args()
    
    log.info("loading")
    data = json.load(open(args.data_prefix + ".data.json", "r"))
    voc_lst = json.load(open(args.data_prefix + ".voc.json", "r"))
    log.info("loaded")
    
    log.info("listing")
    idx_voc_list = list(data)
    log.info("done")
    log.info("shuffling")
    import random
    random.shuffle(idx_voc_list)
    log.info("done")
    
    
    Hw = 500
    Hc = 100
    Vc = len(voc_lst)
    
    log.info("creating nn")
    encdec = CharEncoderDecoder(Hw, Hc, Vc)
    eos_idx = encdec.get_eos_idx()
    
    
#     edec = Encodec(Vi, Hi, Hs, Vo + 1, He)
    if args.load_model:
        serializers.load_npz(args.load_model, encdec)
    
    if args.gpu is not None:
        encdec = encdec.to_gpu(args.gpu)
    log.info("created nn")    
    
    def mb_provider(size = args.mb_size):
        cursor = 0
        while 1:
            if cursor >= len(data):
                cursor = 0
            idxs_seqs = idx_voc_list[cursor: cursor + size]
#             idxs, seqs = zip(*idxs_seqs)
#             idxs = range(cursor, cursor + len(seqs))
            yield idxs_seqs
            cursor += size
    
    def sorter():
        mbp = mb_provider(args.mb_size * 10)
        for seqs in mbp:
#             zipped = zip(seqs, idxs)
            seqs.sort(key = lambda x: len(x))
            for num in range(10):
                if args.mb_size * num >= len(seqs):
                    break
                yield seqs[args.mb_size * num: args.mb_size * (num + 1)]
    
    mbp = sorter() #mb_provider()
    
    if args.optimizer == "adadelta":
        optimizer = optimizers.AdaDelta()
    elif args.optimizer == "adam":
        optimizer = optimizers.Adam()
    elif args.optimizer == "adagrad":
        optimizer = optimizers.AdaGrad(lr = args.learning_rate)
    elif args.optimizer == "sgd":
        optimizer = optimizers.SGD(lr = args.learning_rate)
    elif args.optimizer == "momentum":
        optimizer = optimizers.MomentumSGD(lr = args.learning_rate,
                                           momentum = args.momentum)
    elif args.optimizer == "nesterov":
        optimizer = optimizers.NesterovAG(lr = args.learning_rate,
                                           momentum = args.momentum)
    elif args.optimizer == "rmsprop":
        optimizer = optimizers.RMSprop(lr = args.learning_rate)
    elif args.optimizer == "RMSpropGraves":
        optimizer = optimizers.RMSprop(lr = args.learning_rate,
                                           momentum = args.momentum)    
    else:
        raise NotImplemented
    
#     optim = optimizers.SGD()
    optimizer.setup(encdec)
    optimizer.add_hook(chainer.optimizer.GradientClipping(1.0))
    
    def compute_first_loss():
        idxs_seqs = idx_voc_list[:args.mb_size]
        tgts, masks = make_batch(idxs_seqs, eos_idx, gpu = args.gpu)
        encoded = encdec.encode_batch(tgts, masks)
        loss = encdec.decode_loss_batch(encoded, tgts)
        print "first loss", loss.data
    
    def train_once():
        encdec.zerograds()
        seqs = mbp.next()
        tgts, masks = make_batch(seqs, eos_idx, gpu = args.gpu)
        encoded = encdec.encode_batch(tgts, masks)
        loss = encdec.decode_loss_batch(encoded, tgts)
#         loss = encdec(tgts, tgts)
        loss.backward()
        optimizer.update()
        return loss.data
        
    voc_lst += ["#"]
    num_iter = 0
    log.info("starting training")
    
    try:
        running_loss = 0
        while 1:
            
            this_loss = train_once()
            running_loss += this_loss
            if num_iter%20 == 0:
                print "iter", num_iter
                print "avg trg loss", running_loss / 20
                running_loss = 0
                compute_first_loss()
                for _ in range(3):
                    idx = random.randint(0, len(data))
                    print idx
                    print data[idx]
                    tgts, masks = make_batch([data[idx]], eos_idx, gpu = args.gpu)
                    encoded = encdec.encode_one(tgts)
                    decoded =  encdec.decode_search_one(encoded, 50)
                    print "".join([voc_lst[c] for c in data[idx]])
                    print "".join([voc_lst[int(c)] for c in decoded])
                print
                
                print "paths"
                idx1 = random.randint(0, len(data))
                idx2 = random.randint(0, len(data))
                
                tgts1, masks1 = make_batch([data[idx1]], eos_idx, gpu = args.gpu)
                encoded1 = encdec.encode_one(tgts1)
                decoded1 =  encdec.decode_search_one(encoded1, 50)                
                print "".join([voc_lst[c] for c in data[idx1]])
                print "".join([voc_lst[int(c)] for c in decoded1])
                print
                
                tgts2, masks2 = make_batch([data[idx2]], eos_idx, gpu = args.gpu)
                encoded2 = encdec.encode_one(tgts2)
                decoded2 =  encdec.decode_search_one(encoded2, 50) 
                print "".join([voc_lst[c] for c in data[idx2]])
                print "".join([voc_lst[int(c)] for c in decoded2])
                print
                diff = encoded2 - encoded1
                for i in xrange(21):
                    encoded_p = encoded1 + (i/20.0) * diff
                    decodedp =  encdec.decode_search_one(encoded_p, 50)
                    print i, "".join([voc_lst[int(c)] for c in decodedp])
                print
            num_iter += 1
    finally:
        fn_save = args.save_prefix + ".model.npz"
        log.info("saving model to %s" % fn_save)
        serializers.save_npz(fn_save, encdec)

        
if __name__ == '__main__':
    commandline()
    