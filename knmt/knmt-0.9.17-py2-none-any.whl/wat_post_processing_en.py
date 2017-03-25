
import argparse, codecs
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("fn_in")
parser.add_argument("fn_out")
args = parser.parse_args()

f_in = codecs.open(args.fn_in, encoding = "utf8")
f_out = codecs.open(args.fn_out, "w", encoding = "utf8")


for line in f_in:
    line = line[0].upper() + line[1:]
    f_out.write(line)