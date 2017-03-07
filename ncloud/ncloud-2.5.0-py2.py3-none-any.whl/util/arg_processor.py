# ----------------------------------------------------------------------------
# Copyright 2017 Nervana Systems Inc.
# ----------------------------------------------------------------------------
"""
Helper func for processing args passed in
"""


def process_args(arg_dict, ignore_none=False):
    api_args = {}
    for key, val in arg_dict.items():
        if key != 'config':
            if ignore_none and val is None:
                continue
            api_args[key] = val
    return api_args
