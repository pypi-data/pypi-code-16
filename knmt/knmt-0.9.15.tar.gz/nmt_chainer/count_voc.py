import argparse, codecs
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("filename")
args = parser.parse_args()

f = codecs.open(args.filename, encoding = "utf8")

nb_tokens = 0
token_set = set()

for line in f:
    line = line.strip().split(" ")
    nb_tokens += len(line)
    for w in line:
        token_set.add(w)

print "nb tokens", nb_tokens
print "nb types", len(token_set)