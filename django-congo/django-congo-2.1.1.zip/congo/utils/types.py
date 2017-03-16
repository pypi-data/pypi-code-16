# -*- coding: utf-8 -*-
def str2bool(val):
    return val.lower() in ("yes", "true", "y", "t", "1")

def bool2int(val):
    return 1 if val else 0
