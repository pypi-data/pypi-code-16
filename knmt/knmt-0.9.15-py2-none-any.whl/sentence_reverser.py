import codecs

import argparse
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("src")
parser.add_argument("tgt")
args = parser.parse_args()

f = codecs.open(args.src, encoding = "utf8")
dest = codecs.open(args.tgt, "w", encoding = "utf8")


for line in f:
    line = line.strip().split(" ")
    dest.write(" ".join(line[::-1]) + "\n")
