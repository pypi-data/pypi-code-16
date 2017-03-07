#!/usr/bin/env python
"""Compare validation contexts between two output files.

Helps differentiate differences in classes like true positives or
false positives based on reported context.
"""
from __future__ import print_function
import collections
import shutil
import subprocess
import sys

import numpy as np
from pysam import VariantFile

from bcbio import utils
from bcbio.variation import vcfutils

def main(f1, f2):
    s1 = vcfutils.get_samples(f1)[0]
    s2 = vcfutils.get_samples(f2)[0]
    out_file = "%s_vs_%s.csv" % (s1, s2)
    tmpdir = utils.safe_makedir("%s_vs_%s-tmp" % (s1, s2))
    s1_uniq = extract_unique(f1, f2, tmpdir)
    summarize_context("%s unique" % s1, s1_uniq)
    s2_uniq = extract_unique(f2, f1, tmpdir)
    summarize_context("%s unique" % s2, s2_uniq)
    s1_shared = extract_shared(f1, f2, tmpdir)
    summarize_context("%s shared" % s1, s1_shared)
    s2_shared = extract_shared(f2, f1, tmpdir)
    summarize_context("%s shared" % s2, s2_shared)
    shutil.rmtree(tmpdir)

def summarize_context(sample, vcf_file):
    count = 0
    depths = []
    contexts = collections.defaultdict(int)
    with VariantFile(vcf_file) as val_in:
        for rec in val_in:
            count += 1
            context = rec.info.get("genome_context")
            if context:
                if not isinstance(context, (list, tuple)):
                    context = context.split(",")
                for c in list(set(context)):
                    contexts[c] += 1
            depth = rec.samples.values()[0].get("DP")
            if depth:
                depths.append(depth)
    print("*", sample)
    print("  variant count: %s" % count)
    print("  median depth: %s" % (np.median(depths) if len(depths) > 0 else ""))
    print("  contexts:")
    for n, c in sorted([(n, c) for c, n in contexts.items()], reverse=True):
        print("    %s %s (%0.1f%%)" % (c, n, float(n) / count * 100.0))
    print()

def extract_shared(want_vcf, compare_vcf, tmpdir):
    """Retrieve file of shared variants from want VCF.
    """
    out_file = "%s-shared%s" % (utils.splitext_plus(want_vcf))
    cmd = ("bcftools isec -c all -w 1 -n =2 -O z -o {out_file} {want_vcf} {compare_vcf}")
    subprocess.check_call(cmd.format(**locals()), shell=True)
    return out_file

def extract_unique(want_vcf, compare_vcf, tmpdir):
    """Retrieve file of unique variants from want VCF.
    """
    out_file = "%s-uniq%s" % (utils.splitext_plus(want_vcf))
    cmd = ("bcftools isec -c all -w 1 -n =1 -O z -o {out_file} {want_vcf} {compare_vcf}")
    subprocess.check_call(cmd.format(**locals()), shell=True)
    return out_file

if __name__ == "__main__":
    main(*sys.argv[1:])
