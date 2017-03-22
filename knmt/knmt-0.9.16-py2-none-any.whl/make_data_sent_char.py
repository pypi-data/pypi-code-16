import codecs, json, gzip

import logging

logging.basicConfig()
log = logging.getLogger("vtc:sc")
log.setLevel(logging.INFO)

def commandline():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus")
    parser.add_argument("data_prefix")
    args = parser.parse_args()
    
    f = codecs.open(args.corpus, "r", encoding = "utf8")
    data = []
    dic = {}
    voc_lst = []
    for line in f:
        splitted_line = line.strip().split(" ")
        sentence = []
        for w in splitted_line:
            w_as_seq = []
            for c in w:
                if c not in dic:
                    new_idx = len(dic)
                    voc_lst.append(c)
                    dic[c] = new_idx
                    assert len(voc_lst) == len(dic)
                w_as_seq.append(dic[c])
            sentence.append(w_as_seq)
        data.append(sentence)
            
                
    log.info("nb sentences: %i" % len(data))
    log.info("nb char: %i" % len(voc_lst))
    json.dump(data, gzip.open(args.data_prefix + ".data.json.gzip", "wb", compresslevel = 4))
    json.dump(voc_lst, open(args.data_prefix + ".voc.json", "w"))
        
    
if __name__ == '__main__':
    commandline()
    
        