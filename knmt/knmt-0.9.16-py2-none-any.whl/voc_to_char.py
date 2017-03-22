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
log = logging.getLogger("vtc:vtc")
log.setLevel(logging.INFO)


class Decoder1(Chain):
    def __init__(self, Hi, Hs, Vo):
        assert Hi == Hs
        super(Decoder1, self).__init__(
#             bil = L.Bilinear(Hi, Hs, Hs),
            lstm = L.GRU(Hi, Hi),
            lin_o = L.Linear(Hi, Vo)
        )
        self.Hs = Hi
        self.add_param("initial_st", (Hs,))
        self.initial_st.data[...] = np.random.randn(Hs)
        
    def forward_one_step(self, prev_s, encoded_i):
#         print encoded_i.data.shape
#         print prev_s.data.shape
#         new_s = self.bil(encoded_i, prev_s)
        new_s = self.lstm(prev_s, encoded_i)
        new_s = F.tanh(new_s)
        logits = self.lin_o(new_s)
        return new_s, logits
        
    def __call__(self, encoded_i, target):
        mb_size = encoded_i.data.shape[0]
        prev_s = F.broadcast_to(F.reshape(self.initial_st, (1, -1)), (mb_size, self.Hs))
        loss = 0
        for i in xrange(len(target)):
            prev_s, logits = self.forward_one_step(prev_s, encoded_i)
            local_loss = F.softmax_cross_entropy(logits, target[i])
            loss += local_loss
        return loss
    
    def decode(self, encoded_i, eos_idx):
        prev_s = F.reshape(self.initial_st, (1, -1))
        seq = []
        for i in xrange(50):
            prev_s, logits = self.forward_one_step(prev_s, F.reshape(encoded_i, (1, -1)))
            idx = np.argmax(logits.data)
            seq.append(idx)
            if idx == eos_idx:
                break
        return seq

class Decoder2(Chain):
    def __init__(self, Hi, Hs, He, Vo):
        super(Decoder2, self).__init__(
#             bil = L.Bilinear(Hi, Hs, Hs),
            lstm = L.GRU(Hs, Hi + He),
            lin_o = L.Linear(Hs, Vo),
            emb = L.EmbedID(Vo, Hi)
        )
        self.Hs = Hs
        self.Vo = Vo
        self.Hi = Hi
        self.He = He
        
        self.add_param("initial_st", (Hs,))
        self.initial_st.data[...] = np.random.randn(Hs)
         
        self.add_param("initial_emb_c", (Hi,))
        self.initial_emb_c.data[...] = np.random.randn(Hi)
         
    def forward_one_step(self, prev_s, encoded_i, prev_y):
#         print encoded_i.data.shape
#         print prev_s.data.shape
#         new_s = self.bil(encoded_i, prev_s)
#         emb_c = self.emb(prev_c)
        concatenated = F.concat((encoded_i, prev_y), axis = 1)
        new_s = self.lstm(prev_s, concatenated)
#         new_s = F.tanh(new_s)
        logits = self.lin_o(new_s)
        return new_s, logits
         
    def __call__(self, encoded_i, target):
        xp = cuda.get_array_module(self.initial_st.data)
        mb_size = encoded_i.data.shape[0]
        prev_s = F.broadcast_to(F.reshape(self.initial_st, (1, -1)), (mb_size, self.Hs))
        prev_y = F.broadcast_to(F.reshape(self.initial_emb_c, (1, -1)), (mb_size, self.Hi))
        loss = 0
        prev_c = None
        total_nb_predictions = 0
        for i in xrange(len(target)):
            if prev_c is not None:
                prev_y = self.emb(prev_c)
            prev_s, logits = self.forward_one_step(prev_s, encoded_i, prev_y)
            local_loss = F.softmax_cross_entropy(logits, target[i], normalize = False) * mb_size
            loss += local_loss
            prev_c = target[i]
            total_nb_predictions += xp.sum(target[i].data != -1)
        return loss/ total_nb_predictions
     
    def decode(self, encoded_i, eos_idx):
        xp = cuda.get_array_module(self.initial_st.data)
        prev_s = F.reshape(self.initial_st, (1, -1))
        prev_y = F.reshape(self.initial_emb_c, (1, -1))
        seq = []
        prev_c = None
        for i in xrange(50):
            if prev_c is not None:
                prev_y = self.emb(prev_c)
            prev_s, logits = self.forward_one_step(prev_s, F.reshape(encoded_i, (1, -1)), prev_y)
            idx = np.argmax(logits.data)
            seq.append(idx)
            if idx == eos_idx:
                break
            prev_c = Variable(xp.array([idx], dtype = xp.int32), volatile = "auto")
        return seq

    

class Encodec(Chain):
    def __init__(self, Vi, Hi, Hs, Vo, He):
        super(Encodec, self).__init__(
            emb = L.EmbedID(Vi, He),
#             dec = Decoder1(Hi, Hs, Vo)
            dec = Decoder2(Hi, Hs, He, Vo)
        )
    def __call__(self, inpt, target):
        rep = self.emb(inpt)
        loss = self.dec(rep, target)
        return loss
    def decode(self, num, eos_idx):
        inpt = Variable(np.array([num], dtype = np.int32), volatile = "on")
        rep = self.emb(inpt)
        return self.dec.decode(rep, eos_idx)

def make_batch(idxs, seqs, eos_idx, gpu = None):
    idxs_np = np.array(idxs, dtype = np.int32)
    if gpu is not None:
        idxs_np = cuda.to_gpu(idxs_np, gpu)
    inpt = Variable(idxs_np)
    
    max_len = max(len(s) for s in seqs)
    targets = []
    for i in xrange(max_len):
        cur_var = []
        for j in xrange(len(seqs)):
            if i < len(seqs[j]):
                cur_var.append(seqs[j][i])
            elif i == len(seqs[j]):
                cur_var.append(eos_idx)
            else:
                cur_var.append(-1)
        seq_i = np.array(cur_var, dtype = np.int32)
        if gpu is not None:
            seq_i = cuda.to_gpu(seq_i, gpu)
        targets.append(Variable(seq_i))
    return inpt, targets
    

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
    idx_voc_list = list(enumerate(data))
    log.info("done")
    log.info("shuffling")
    import random
    random.shuffle(idx_voc_list)
    log.info("done")
    
    He = 150
    Hi = 100
    Hs = 150
    Vo = len(voc_lst)
    Vi = len(data)
    eos_idx = Vo
    
    log.info("creating nn")
#     edec = Encodec(Vi, Hi, Hs, Vo + 1)
    edec = Encodec(Vi, Hi, Hs, Vo + 1, He)
    if args.load_model:
        serializers.load_npz(args.load_model, edec)
    
    if args.gpu is not None:
        edec = edec.to_gpu(args.gpu)
    log.info("created nn")    
    
    def mb_provider(size = args.mb_size):
        cursor = 0
        while 1:
            if cursor >= len(data):
                cursor = 0
            idxs_seqs = idx_voc_list[cursor: cursor + size]
            idxs, seqs = zip(*idxs_seqs)
#             idxs = range(cursor, cursor + len(seqs))
            yield seqs, idxs
            cursor += size
    
    def sorter():
        mbp = mb_provider(args.mb_size * 10)
        for seqs, idxs in mbp:
            zipped = zip(seqs, idxs)
            zipped.sort(key = lambda x: len(x[0]))
            sorted_seqs, sorted_idxs = zip(*zipped)
            for num in range(10):
                if args.mb_size * num >= len(sorted_seqs):
                    break
                yield sorted_seqs[args.mb_size * num: args.mb_size * (num + 1)], sorted_idxs[args.mb_size * num: args.mb_size * (num + 1)]
    
    
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
    optimizer.setup(edec)
    optimizer.add_hook(chainer.optimizer.GradientClipping(1.0))
    
    def compute_first_loss():
        idxs_seqs = idx_voc_list[:args.mb_size]
        idxs, seqs = zip(*idxs_seqs)
        inpts, tgts = make_batch(idxs, seqs, eos_idx, gpu = args.gpu)
        loss = edec(inpts, tgts)
        print "first loss", loss.data
    
    def train_once():
        edec.zerograds()
        seqs, idxs = mbp.next()
        inpts, tgts = make_batch(idxs, seqs, eos_idx, gpu = args.gpu)
        loss = edec(inpts, tgts)
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
                    print edec.decode(idx, eos_idx)
                    print "".join([voc_lst[c] for c in data[idx]])
                    print "".join([voc_lst[int(c)] for c in edec.decode(idx, eos_idx)])
                print
            num_iter += 1
    finally:
        fn_save = args.save_prefix + ".model.npz"
        log.info("saving model to %s" % fn_save)
        serializers.save_npz(fn_save, edec)

        
if __name__ == '__main__':
    commandline()