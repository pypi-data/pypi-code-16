#!/usr/bin/env python
"""make_data.py: prepare data for training"""
__author__ = "Fabien Cromieres"
__license__ = "undecided"
__version__ = "1.0"
__email__ = "fabien.cromieres@gmail.com"
__status__ = "Development"

import collections
import logging
import codecs
import json
import operator
import os.path
import gzip

from utils import ensure_path
# import h5py

logging.basicConfig()
log = logging.getLogger("rnns:make_data")
log.setLevel(logging.INFO)


class Converter(object):
    def convert(self, seq):
        pass
    def deconvert(self, seq):
        pass
    def get_special_token(self, id_special = 0):
        pass
    def to_serializable(self):
        pass
    @staticmethod
    def from_serializable(self):
        pass
    
class Converter(object):
    def convert_input(self, seq):
        pass
    def deconvert_input(self, seq):
        pass
    def get_special_token_input(self, id_special = 0):
        pass
    def convert_output(self, seq):
        pass
    def deconvert_output(self, seq):
        pass
    def get_special_token_tgt(self, id_special = 0):
        pass    
    def convert_training_item(self):
        pass
    def save_to(self, fn):
        pass
    @staticmethod
    def load_from(self, fn):
        pass

class SrcTgtConverterSimple(object):
    def convert_src(self, seq):
        pass
    def deconvert_src(self, seq):
        pass
    def get_special_token_src(self, id_special = 0):
        pass
    def convert_tgt(self, seq):
        pass
    def deconvert_tgt(self, seq):
        pass
    def get_special_token_tgt(self, id_special = 0):
        pass    
    def save_to(self, fn):
        pass
    def load_from(self, fn):
        pass



class Indexer(object):
    def __init__(self, unk_tag = "#UNK#"):
        self.dic = {}
        self.lst = []
        self.finalized = False
        self._unk_idx = None
        self.unk_tag = unk_tag
        
    @property
    def unk_idx(self):
        if self._unk_idx is None:
            self.finalized = True
            self._unk_idx = len(self.lst)
            self.lst.append(self.unk_tag)
            assert self.unk_tag not in self.dic
            self.dic[self.unk_tag] = self._unk_idx
        return self._unk_idx
        
    def finalize(self):
        self.finalized = True
        
    def get_special_idx(self, id_special = 0):
        assert self.finalized
        return len(self.lst) + id_special
        
    def convert(self, seq):
        assert len(self.dic) == len(self.lst)
        unk_idx = self.unk_idx
#         res = np.empty( (len(seq),), dtype = np.int32)
        res = [None] * len(seq)
        for pos, w in enumerate(seq):
            if w in self.dic:
                idx = self.dic.get(w, unk_idx)
                res[pos] = idx
        return res
    
#     def convert_with_unk_count(self, seq):
#         assert len(self.dic) == len(self.lst)
#         unk_idx = len(self.lst)
# #         res = np.empty( (len(seq),), dtype = np.int32)
#         res = [None] * len(seq)
#         unk_count = 0
#         for pos, w in enumerate(seq):
#             if w in self.dic:
#                 idx = self.dic[w]
#             else:
#                 idx = unk_idx
#                 unk_count += 1
#             res[pos] = idx
#         return res, unk_count
    
    def __len__(self):
        assert len(self.dic) == len(self.lst)
        return len(self.lst)
    
    @staticmethod
    def make_from_list(voc_lst):
        res = Indexer()
        res.lst = list(voc_lst)
        for idx, w in enumerate(voc_lst):
            res.dic[w] = idx
        return res
    
    def assign_index_to_voc(self, voc_iter, all_should_be_new = False):
        for w in voc_iter:
            self.add_word(w, should_be_new = all_should_be_new)
                
    def add_word(self, w, should_be_new = False):
        if w not in self.dic:
            self.dic[w] = len(self.lst)
            self.lst.append(w)
            assert len(self.lst) == len(self.dic)
        else:
            assert not should_be_new      
              

def build_index(fn, voc_limit = None, max_nb_ex = None):
    f = codecs.open(fn, encoding= "utf8")
    counts = collections.defaultdict(int)
    for num_ex, line in enumerate(f):
        if max_nb_ex is not None and num_ex >= max_nb_ex:
            break
        line =line.strip().split(" ")
        for w in line:
            counts[w] += 1
    
      
    sorted_counts = sorted(counts.items(), key = operator.itemgetter(1), reverse = True)
    
    res = Indexer()
    
    for idx,(w, cnt) in enumerate(sorted_counts[:voc_limit]):
        res.dic[w] = idx
        res.lst.append(w)
        assert len(res.lst) == len(res.dic)
    
    return res
    
def build_dataset_one_side(src_fn, src_voc_limit = None, max_nb_ex = None, dic_src = None):
    if dic_src is None:
        log.info("building src_dic")
        dic_src = build_index(src_fn, src_voc_limit, max_nb_ex)
    
    log.info("start indexing")
    
    src = codecs.open(src_fn, encoding= "utf8")
    
    res = []
    
    num_ex = 0
    total_token_src = 0
    total_count_unk_src = 0
    while 1:
        if max_nb_ex is not None and num_ex >= max_nb_ex:
            break
        
        line_src = src.readline()
        
        if len(line_src) == 0:
            break
        
        line_src = line_src.strip().split(" ")
        
        seq_src = dic_src.convert(line_src)
        unk_cnt_src = sum(idx == dic_src.unk_idx for idx in seq_src)

        total_count_unk_src += unk_cnt_src
        
        total_token_src += len(seq_src)

        res.append(seq_src)
        num_ex += 1
        
    return res, dic_src, total_count_unk_src, total_token_src, num_ex
 
def build_dataset(src_fn, tgt_fn, src_voc_limit = None, tgt_voc_limit = None, max_nb_ex = None, dic_src = None, dic_tgt = None):
    if dic_src is None:
        log.info("building src_dic")
        dic_src = build_index(src_fn, src_voc_limit, max_nb_ex)
        
    if dic_tgt is None:
        log.info("building tgt_dic")
        dic_tgt = build_index(tgt_fn, tgt_voc_limit, max_nb_ex)
    
    
    log.info("start indexing")
    
    src = codecs.open(src_fn, encoding= "utf8")
    tgt = codecs.open(tgt_fn, encoding= "utf8")
    
    res = []
    
    num_ex = 0
    total_token_src = 0
    total_token_tgt = 0
    total_count_unk_src = 0
    total_count_unk_tgt = 0
    while 1:
        if max_nb_ex is not None and num_ex >= max_nb_ex:
            break
        
        line_src = src.readline()
        line_tgt = tgt.readline()
        
        if len(line_src) == 0:
            assert len(line_tgt) == 0
            break
        
        line_src = line_src.strip().split(" ")
        line_tgt = line_tgt.strip().split(" ")
        
        seq_src, unk_cnt_src= dic_src.convert_with_unk_count(line_src)
        seq_tgt, unk_cnt_tgt = dic_tgt.convert_with_unk_count(line_tgt)

        total_count_unk_src += unk_cnt_src
        total_count_unk_tgt += unk_cnt_tgt
        
        total_token_src += len(seq_src)
        total_token_tgt += len(seq_tgt)

        res.append((seq_src, seq_tgt))
        num_ex += 1
        
    return res, dic_src, dic_tgt, total_count_unk_src, total_count_unk_tgt, total_token_src, total_token_tgt, num_ex

def build_dataset_with_align_info(src_fn, tgt_fn, align_fn, 
                                  src_voc_limit = None, tgt_voc_limit = None, max_nb_ex = None, 
                                  dic_src = None, dic_tgt = None,
                                  invert_alignment_links = False):
    from aligned_parse_reader import load_aligned_corpus
    corpus = load_aligned_corpus(
        src_fn, tgt_fn, align_fn, skip_empty_align = True, invert_alignment_links = invert_alignment_links)
    
    # first find the most frequent words
    counts_src = collections.defaultdict(int)
    counts_tgt = collections.defaultdict(int)
    for num_ex, (sentence_src, sentence_tgt, alignment) in enumerate(corpus):
        if max_nb_ex is not None and num_ex >= max_nb_ex:
            break
        for pos, w in enumerate(sentence_src):
            counts_src[w] += 1
        for w in sentence_tgt:
            counts_tgt[w] += 1
    sorted_counts_src = sorted(counts_src.items(), key = operator.itemgetter(1), reverse = True)
    sorted_counts_tgt = sorted(counts_tgt.items(), key = operator.itemgetter(1), reverse = True)
    
    dic_src = Indexer()       
    dic_src.assign_index_to_voc((w for w, _ in sorted_counts_src[:src_voc_limit]), all_should_be_new = True)
        
    dic_tgt = Indexer()
    dic_tgt.assign_index_to_voc((w for w, _ in sorted_counts_tgt[:tgt_voc_limit]), all_should_be_new = True)
    
    src_unk_tag = "#S_UNK_%i#!"
    tgt_unk_tag = "#T_UNK_%i#!"
    
    corpus = load_aligned_corpus(
        src_fn, tgt_fn, align_fn, skip_empty_align = True, invert_alignment_links = invert_alignment_links)
    
    total_token_src = 0
    total_token_tgt = 0
    total_count_unk_src = 0
    total_count_unk_tgt = 0
    res = []
    fertility_counts = collections.defaultdict(lambda:collections.defaultdict(int))
    for num_ex, (sentence_src, sentence_tgt, alignment) in enumerate(corpus):
        if max_nb_ex is not None and num_ex >= max_nb_ex:
            break
        local_fertilities = {}
        local_alignments = {}
        for left, right in alignment:
            for src_pos in left:
                local_fertilities[src_pos] = len(right)
            for tgt_pos in right:
                assert tgt_pos not in local_alignments
                local_alignments[tgt_pos] = left[0]
    
        seq_idx_src = []
        for pos, w in enumerate(sentence_src):
            total_token_src += 1
            if w not in dic_src:
                total_count_unk_src += 1
                fertility = local_fertilities.get(pos, 0)
                fertility_counts[w][fertility] += 1
                w_unk = src_unk_tag % fertility
                if w_unk not in dic_src:
                    dic_src.add_word(w_unk)
            assert w in dic_src
            seq_idx_src.append(dic_src[w])

        seq_idx_tgt = []
        for pos, w in enumerate(sentence_tgt):
            total_token_tgt += 1
            if w not in dic_tgt:
                total_count_unk_tgt += 1
                aligned_pos = local_alignments.get(pos, -1)
                w_unk = tgt_unk_tag % aligned_pos
                if w_unk not in dic_tgt:
                    dic_tgt.add_word(w_unk)
            assert w in dic_tgt
            seq_idx_tgt.append(dic_tgt[w])                
    
        res.append((seq_idx_src, seq_idx_tgt))
    
    src_unk_voc_to_fertility = {}
    for w in fertility_counts:
        most_common_fertility = sorted(src_unk_voc_to_fertility[w].items(), key = operator.itemgetter(1), reverse = True)[0]
        src_unk_voc_to_fertility[w] = most_common_fertility
    
    return (res, dic_src, dic_tgt, src_unk_voc_to_fertility,
            total_count_unk_src, total_count_unk_tgt, total_token_src, total_token_tgt, num_ex)

def cmdline():
    import sys
    import argparse
    parser = argparse.ArgumentParser(description= "Prepare training data.", 
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("src_fn", help = "source language text file for training data")
    parser.add_argument("tgt_fn", help = "target language text file for training data")
    parser.add_argument("save_prefix", help = "created files will be saved with this prefix")
    parser.add_argument("--src_voc_size", type = int, default = 32000, 
                        help = "limit source vocabulary size to the n most frequent words")
    parser.add_argument("--tgt_voc_size", type = int, default = 32000,
                        help = "limit target vocabulary size to the n most frequent words")
#     parser.add_argument("--add_to_valid_set_every", type = int)
#     parser.add_argument("--shuffle", default = False, action = "store_true")
#     parser.add_argument("--enable_fast_shuffle", default = False, action = "store_true")
    parser.add_argument("--max_nb_ex", type = int, help = "only use the first MAX_NB_EX examples")
    
    parser.add_argument("--test_src", help = "specify a source test set")
    parser.add_argument("--test_tgt", help = "specify a target test set")
    
    parser.add_argument("--dev_src", help = "specify a source dev set")
    parser.add_argument("--dev_tgt", help = "specify a target dev set")
    
    parser.add_argument("--use_voc", help = "specify an exisiting vocabulary file")
    args = parser.parse_args()
    
    if not ((args.test_src is None) == (args.test_tgt is None)):
        print >>sys.stderr, "Command Line Error: either specify both --test_src and --test_tgt or neither"
        sys.exit(1)
    
    if not ((args.dev_src is None) == (args.dev_tgt is None)):
        print >>sys.stderr, "Command Line Error: either specify both --test_src and --test_tgt or neither"
        sys.exit(1)
    
    save_prefix_dir, save_prefix_fn = os.path.split(args.save_prefix)
    ensure_path(save_prefix_dir)
    
    
    config_fn = args.save_prefix + ".data.config"
    voc_fn = args.save_prefix + ".voc"
    data_fn = args.save_prefix + ".data.json.gz"
#     valid_data_fn = args.save_prefix + "." + args.model + ".valid.data.npz"
    
    already_existing_files = []
    for filename in [config_fn, voc_fn, data_fn]:#, valid_data_fn]:
        if os.path.exists(filename):
            already_existing_files.append(filename)
    if len(already_existing_files) > 0:
        print "Warning: existing files are going to be replaced: ",  already_existing_files
        raw_input("Press Enter to Continue")
        
        
    def load_data(src_fn, tgt_fn, max_nb_ex = None, dic_src = None, dic_tgt = None):
        
        training_data, dic_src, dic_tgt, total_count_unk_src, total_count_unk_tgt, total_token_src, total_token_tgt, nb_ex = build_dataset(
                                            src_fn, tgt_fn, src_voc_limit = args.src_voc_size, 
                                            tgt_voc_limit = args.tgt_voc_size, max_nb_ex = max_nb_ex, 
                                            dic_src = dic_src, dic_tgt = dic_tgt)
        
        log.info("%i sentences loaded"%nb_ex)
        
        log.info("size dic src: %i"%len(dic_src))
        log.info("size dic tgt: %i"%len(dic_tgt))
        
        log.info("#tokens src: %i   of which %i (%f%%) are unknown"%(total_token_src, total_count_unk_src, 
                                                                     float(total_count_unk_src * 100) / total_token_src))
        
        log.info("#tokens tgt: %i   of which %i (%f%%) are unknown"%(total_token_tgt, total_count_unk_tgt, 
                                                                 float(total_count_unk_tgt * 100) / total_token_tgt))
        
        return training_data, dic_src, dic_tgt
    
    dic_src = None
    dic_tgt = None
    if args.use_voc is not None:  
        log.info("loading voc from %s"% args.use_voc)
        src_voc, tgt_voc = json.load(open(args.use_voc))
        dic_src = Indexer.make_from_list(src_voc)
        dic_tgt = Indexer.make_from_list(tgt_voc)
    
    log.info("loading training data from %s and %s"%(args.src_fn, args.tgt_fn))
    training_data, dic_src, dic_tgt = load_data(args.src_fn, args.tgt_fn, max_nb_ex = args.max_nb_ex,
                                                dic_src = dic_src, dic_tgt = dic_tgt)
    
    test_data = None
    if args.test_src is not None:
        log.info("loading test data from %s and %s"%(args.test_src, args.test_tgt))
        test_data, test_dic_src, test_dic_tgt = load_data(args.test_src, args.test_tgt, dic_src = dic_src, dic_tgt = dic_tgt)
        
        assert test_dic_src is dic_src
        assert test_dic_tgt is dic_tgt

    dev_data = None
    if args.dev_src is not None:
        log.info("loading dev data from %s and %s"%(args.dev_src, args.dev_tgt))
        dev_data, dev_dic_src, dev_dic_tgt = load_data(args.dev_src, args.dev_tgt, dic_src = dic_src, dic_tgt = dic_tgt)
        
        assert dev_dic_src is dic_src
        assert dev_dic_tgt is dic_tgt

#     if args.shuffle:
#         log.info("shuffling data")
#         if args.enable_fast_shuffle:
#             shuffle_in_unison_faster(data_input, data_target)
#         else:
#             data_input, data_target = shuffle_in_unison(data_input, data_target)
    log.info("saving config to %s"%config_fn)
    json.dump(args.__dict__, open(config_fn, "w"), indent=2, separators=(',', ': '))

    log.info("saving voc to %s"%voc_fn)
    json.dump([dic_src.lst, dic_tgt.lst], open(voc_fn, "w"))
    
    log.info("saving train_data to %s"%data_fn)
    data_all = {"train": training_data}
    if test_data is not None:
        data_all["test"] = test_data
    if dev_data is not None:
        data_all["dev"] = dev_data
    json.dump(data_all, gzip.open(data_fn, "wb"), indent=2, separators=(',', ': '))
#     fh5 = h5py.File(args.save_data_to_hdf5, 'w')
#     train_grp = fh5.create_group("train")
#     train_grp.attrs["size"] = len(training_data)
#     for i in range(len(training_data)):
#         train_grp.create_dataset("s%i"%i, data = training_data[i][0], compression="gzip")
#         train_grp.create_dataset("t%i"%i, data = training_data[i][1], compression="gzip")
    
#     if args.add_to_valid_set_every:
#         log.info("saving valid_data to %s"%valid_data_fn)
#         np.savez_compressed(open(valid_data_fn, "wb"), data_input = data_input_valid, data_target = data_target_valid)
        
if __name__ == '__main__':
    cmdline()