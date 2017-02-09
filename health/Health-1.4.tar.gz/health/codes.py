import os
import cPickle

# Make package globals
this_dir, this_file = os.path.split(__file__)
path = os.path.join(this_dir, 'data', 'icd2desc.p')
icd2desc = cPickle.load(open(path, 'rb'))
path = os.path.join(this_dir, 'data', 'icd2ccs.p')
icd2ccs = cPickle.load(open(path, 'rb'))
path = os.path.join(this_dir, 'data', 'ccs2icd.p')
ccs2icd = cPickle.load(open(path, 'rb'))
path = os.path.join(this_dir, 'data', 'ccs2desc.p')
ccs2desc = cPickle.load(open(path, 'rb'))

