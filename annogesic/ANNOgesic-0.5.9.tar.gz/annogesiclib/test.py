import argparse
from gff3 import Gff3Parser

__author__ = "Sung-Huan Yu <sung-huan.yu@uni-wuerzburg.de>"
__email__ = "sung-huan.yu@uni-wuerzburg.de"

parser = argparse.ArgumentParser()
parser.add_argument("-i","--input_file",help="input file")
parser.add_argument("-o","--output_file",help="output file")
parser.add_argument("-t","--tss_file",help="output file")
args = parser.parse_args()

def main():
    '''generate the table of promoter based on MEME'''
    tsss = []
    gff_f = open(args.tss_file, "r")
    for entry in Gff3Parser().entries(gff_f):
        tsss.append(entry)
    out = open(args.output_file, "w")
    out.write("\t".join(["strain", "TSS_position",
                         "TSS_strand", "Motif"]) + "\n")
    start = False
    num = 1
    with open(args.input_file) as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("*"):
                start = True
                motif = "MOTIF_" + str(num)
                num += 1
            elif len(line) == 0:
                start = False
            elif start:
                datas = line.split(" ")[0].split("_")
                for tss in tsss:
                    if ("_".join(datas[2:]) in tss.seq_id) and (
                            datas[0] == str(tss.start)) and (
                            datas[1] == tss.strand):
                        out.write("\t".join([tss.seq_id, datas[0],
                                  datas[1], motif]) + "\n")
                        
if __name__ == "__main__":
    main()
