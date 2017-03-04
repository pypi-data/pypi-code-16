"""Functions reused within command-line implementations."""
from __future__ import absolute_import, division, print_function

import logging

from . import tabio


def load_het_snps(vcf_fname, sample_id, normal_id, min_variant_depth,
                  zygosity_freq, tumor_boost=False):
    if vcf_fname is None:
        return None
    varr = tabio.read(vcf_fname, 'vcf',
                      sample_id=sample_id, # or tumor_cn.sample_id,
                      normal_id=normal_id,
                      min_depth=min_variant_depth,
                      skip_somatic=True)
    if zygosity_freq is not None:
        varr = varr.zygosity_from_freq(zygosity_freq, 1 - zygosity_freq)
    orig_len = len(varr)
    varr = varr.heterozygous()
    logging.info("Kept %d heterozygous of %d VCF records",
                 len(varr), orig_len)
    # TODO use/explore tumor_boost option
    if tumor_boost:
        varr['alt_freq'] = varr.tumor_boost()
    return varr


def verify_sex_arg(cnarr, sex_arg, is_male_reference):
    is_sample_female = cnarr.guess_xx(is_male_reference, verbose=False)
    if sex_arg:
        is_sample_female_given = (sex_arg.lower() not in ["y", "m", "male"])
        if is_sample_female != is_sample_female_given:
            logging.info("Sample sex specified as %s "
                         "but chrX copy number looks like %s",
                         sex_arg,
                         "female" if is_sample_female else "male")
            is_sample_female = is_sample_female_given
    logging.info("Treating sample sex as %s",
                 "female" if is_sample_female else "male")
    return is_sample_female
