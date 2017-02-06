import numpy as np
import chainer
from chainer import cuda, Function, gradient_check, Variable, optimizers, serializers, utils
from chainer import Link, Chain, ChainList
import chainer.functions as F
import chainer.links as L

import logging
logging.basicConfig()
log = logging.getLogger("char_o")
log.setLevel(logging.INFO)

class CharOutput(Chain):
    def __init__(self, max_length, input_size, nb_char):
        super(CharOutput, self).__init__(
            lin_o = L.Linear(input_size, nb_char),
#             lin_h = L.Linear(input_size, input_size)
            
        )
        self.add_param("positions_emb", (1, max_length, input_size))
        self.positions_emb.data[...] = np.random.randn(1, max_length, input_size).astype(np.float32)
        self.input_size = input_size
        self.max_length = max_length
        self.nb_char = nb_char
        
    def compute_flat_logits(self, inpt):
        mb_size, inpt_size = inpt.data.shape
        assert inpt_size == self.input_size
        
        broadcasted_i = F.broadcast_to(F.reshape(inpt, (mb_size, 1, self.input_size)), 
                                       (mb_size, self.max_length, self.input_size))
        broadcasted_p = F.broadcast_to(self.positions_emb, (mb_size, self.max_length, self.input_size))

        h = F.reshape(F.relu(broadcasted_i + broadcasted_p), (self.max_length * mb_size, self.input_size))

#         h = F.relu(self.lin_h(h))
        
        logits = self.lin_o(h)
        
        return logits
    
    def compute_log_prob(self, inpt, target):
        mb_size, inpt_size = inpt.data.shape
        assert inpt_size == self.input_size
        logits = self.compute_flat_logits(inpt)
        loss = F.softmax_cross_entropy(logits, F.reshape(target, (self.max_length * mb_size,)))
        return loss
    
    def decode(self, inpt):
        mb_size, inpt_size = inpt.data.shape
        logits = self.compute_flat_logits(inpt)
        reshaped_logits = F.reshape(logits, (mb_size, self.max_length, self.nb_char))
        res = self.xp.argmax(reshaped_logits.data, axis = 2)
        return res
        
class CharStore(Chain):
    def __init__(self, max_length, input_size, nb_char, nb_words):
        super(CharStore, self).__init__(
            word_emb = L.EmbedID(nb_words, input_size),
            char_sm = CharOutput(max_length, input_size, nb_char)
        )
        
    def compute_loss(self, inpt, target):
        i_emb = self.word_emb(inpt)
        loss = self.char_sm.compute_log_prob(i_emb, target)
        return loss
    
    def decode(self, inpt):
        i_emb = self.word_emb(inpt)
        res = self.char_sm.decode(i_emb)
        return res
    
    def decode_path(self, inpt1, inpt2, step = 0.1):
        i_emb_1 = self.word_emb(inpt1)
        i_emb_2 = self.word_emb(inpt2)
        
        res = []
        
        coeffs_list = []
        coeff = 0
        while 1:
            if coeff > 1:
                coeff = 1
            coeffs_list.append(coeff)
            if coeff >= 1:
                break
            coeff += step
            
        for coeff in coeffs_list:
            ii = i_emb_1 + coeff * (i_emb_2 - i_emb_1)
            res.append(self.char_sm.decode(ii))
        return res
    
def test1():
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("voc_file")
    parser.add_argument("dest")
    parser.add_argument("--gpu", type = int)
    parser.add_argument("--raw_voc", default = False, action = "store_true")
    args = parser.parse_args()
    
    log.info("loading voc from %s" % args.voc_file)
    if args.raw_voc:
        import codecs
        f = codecs.open(args.voc_file, "r", encoding = "utf8")
        e_voc = [w.strip() for w in f]
    else:
        import json
        voc = json.load(open(args.voc_file))
        e_voc = voc[1]
    
    char_set = set(c for w in e_voc for c in w)
    char_decode = list(char_set) + [None]
    char_encode = dict((c, idx) for (idx,c) in enumerate(char_decode))
    
    nb_words = len(e_voc)
    nb_char = len(char_decode)
    max_length = 20
    input_size = 500
    
    cs = CharStore(max_length, input_size, nb_char, nb_words)
    
    with cuda.get_device(args.gpu):
    
        if args.gpu is not None:
            cs.to_gpu(args.gpu)
        
        data_i = np.arange(nb_words, dtype = np.int32)
        
        data_t = np.empty((nb_words, max_length), dtype = np.int32)
        for i, w in enumerate(e_voc):
            for k in xrange(max_length):
                if k < len(w):
                    data_t[i][k] = char_encode[w[k]]
                else:
                    data_t[i][k] = char_encode[None]
                    
        def shuffle_in_unison_inplace(a, b):
            assert len(a) == len(b)
            p = np.random.permutation(len(a))
            return a[p], b[p]
    
        data_i, data_t = shuffle_in_unison_inplace(data_i, data_t)
        
        def mb_provider(mb_size = 256):
            cursor = 0
            while 1:
                if cursor >= len(data_i):
                    cursor = 0
                if args.gpu is not None:
                    yield (
                           Variable(cuda.to_gpu(data_i[cursor : cursor + mb_size], args.gpu)),
                           Variable(cuda.to_gpu(data_t[cursor : cursor + mb_size], args.gpu))
                           )
                else:
                    yield Variable(data_i[cursor : cursor + mb_size]), Variable(data_t[cursor : cursor + mb_size])
                cursor += mb_size
        
        mbp = mb_provider()
        optimizer = optimizers.Adam()
        optimizer.setup(cs)
        
        def decode_code(code):
            code = cuda.to_cpu(code)
            for mbi in xrange(len(code)):
                print mbi, ":",
                for idx in code[mbi]:
                    print char_decode[idx],
                print "  |||  ",
            print
                
        def train_once(verbose = False):
            i,t = mbp.next()
            cs.zerograds()
            loss = cs.compute_loss(i, t)
            if verbose:
                print loss.data
            loss.backward()
            optimizer.update()
            
            if verbose:
                x = np.random.randint(0, nb_words)
            
                orig = data_i[x]
                print e_voc[orig]
                if args.gpu is not None:
                    this_i = Variable(cuda.to_gpu(np.array([orig], dtype = np.int32), args.gpu), volatile = "on")
                else:
                    this_i = Variable(np.array([orig], dtype = np.int32), volatile = "on")
                    
                decode_code(cs.decode(this_i))
    #             decoded = cuda.to_cpu(cs.decode(this_i))
    #             for idx in decoded[0]:
    #                 print char_decode[idx],
    #             print
                
                x2 = np.random.randint(0, nb_words)
            
                orig2 = data_i[x2]
                print e_voc[orig2]
                if args.gpu is not None:
                    this_i2 = Variable(cuda.to_gpu(np.array([orig2], dtype = np.int32), args.gpu), volatile = "on")
                else:
                    this_i2 = Variable(np.array([orig2], dtype = np.int32), volatile = "on")
                    
                print "  PATH"
                for interm in cs.decode_path(this_i, this_i2, 0.1):
                    decode_code(interm)
                print "END PATH"
                
            
        try:
            for i in xrange(300000):
                if i%1000 == 0:
                    print "i", i
                train_once(i%1000 == 0)
        except KeyboardInterrupt:
            serializers.save_npz(args.dest, cs.char_sm)
    
if __name__ == '__main__':
    test1()