import codecs, json

import logging

logging.basicConfig()
log = logging.getLogger("vtc:make_data")
log.setLevel(logging.INFO)

def commandline():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus")
    parser.add_argument("data_prefix")
    args = parser.parse_args()
    
    f = codecs.open(args.corpus, "r", encoding = "utf8")
    voc = set()
    for line in f:
        splitted_line = line.strip().split(" ")
        for w in splitted_line:
            voc.add(w)
            
    dic = {}
    voc_lst = []
    data = []
    for w in voc:
        seq = []
        for c in w:
            if c not in dic:
                new_idx = len(dic)
                voc_lst.append(c)
                dic[c] = new_idx
                assert len(voc_lst) == len(dic)
            seq.append(dic[c])
        data.append(seq)
                
    log.info("voc size: %i" % len(data))
    log.info("nb char: %i" % len(voc_lst))
    json.dump(data, open(args.data_prefix + ".data.json", "w"))
    json.dump(voc_lst, open(args.data_prefix + ".voc.json", "w"))
        
    
if __name__ == '__main__':
    commandline()
    
        