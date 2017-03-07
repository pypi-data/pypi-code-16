#!/usr/bin/env python
"""Split a UMI grouped file into single and duplicated reads.
"""
import os
import sys

import pysam

def main(in_file):
    out_file_single = "%s-single%s" % os.path.splitext(in_file)
    out_file_multi = "%s-multi%s" % os.path.splitext(in_file)

    in_recs = pysam.AlignmentFile(in_file, "rb")
    out_single = pysam.AlignmentFile(out_file_single, "wb", template=in_recs)
    out_multi = pysam.AlignmentFile(out_file_multi, "wb", template=in_recs)
    cur_recs = []
    cur_group = None
    for rec in in_recs:
        mi = rec.get_tag("MI")
        if mi != cur_group:
            if cur_recs:
                write_group(cur_recs, out_single, out_multi)
            cur_recs = [rec]
            cur_group = mi
        else:
            cur_recs.append(rec)

    if cur_recs:
        write_group(cur_recs, out_single, out_multi)

def write_group(cur_recs, out_single, out_multi):
    for rec in cur_recs:
        if len(cur_recs) == 2:
            out_single.write(rec)
        else:
            out_multi.write(rec)

if __name__ == "__main__":
    main(sys.argv[1])
