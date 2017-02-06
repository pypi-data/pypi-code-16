from pyknp import Juman
import codecs

import logging

logging.basicConfig()
log = logging.getLogger("resegment")
log.setLevel(logging.INFO)

def commandline():
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("src")
    parser.add_argument("out")
    parser.add_argument("port", type = int)
    args = parser.parse_args()
    
    src = codecs.open(args.src, encoding = "utf8")
    dest = codecs.open(args.out, "w", encoding = "utf8")
    
    juman = Juman(server='localhost', port=args.port)
    
    for line in src:
        line = line.strip()
        if len(line) == 0:
            dest.write("\n")
            continue
        line = "".join(line.split(" "))
        try:
            analysed = juman.analysis(line)
        except (UnicodeEncodeError, IndexError):
            log.warn("could not segment %s"%line)
            dest.write("\n")
            continue
        splitted = [mrph.midasi for mrph in analysed.mrph_list()]
        dest.write(" ".join(splitted) + "\n")
        
if __name__ == '__main__':
    commandline()