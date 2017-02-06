import argparse, codecs
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("filename")
parser.add_argument("dest")
args = parser.parse_args()

f = codecs.open(args.filename, encoding = "utf8")
dest = codecs.open(args.dest, "w", encoding = "utf8")

for line in f:
    line = line.strip().split(" ")
    new_line = []
    for w in line:
        if w.startswith("-LSB-") and len(w) > 5:
            new_line.append(w[:5])
            new_line.append(w[5:])
        else:
            new_line.append(w)
    dest.write(" ".join(new_line) + "\n")
