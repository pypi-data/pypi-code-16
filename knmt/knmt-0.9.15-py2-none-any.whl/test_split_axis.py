

 #!/usr/bin/python3

import os
os.environ['CHAINER_TYPE_CHECK'] = '0'
import numpy
import chainer
from chainer import functions as F

import time
from contextlib import contextmanager

@contextmanager
def time_block(name, proc=False):
    startTime = time.time()
    print name,
    yield
    elapsedTime = time.time() - startTime
    print ' finished in {0:.2f}ms'.format(elapsedTime*1000)

x = chainer.Variable(numpy.random.random((1024,1024)),volatile='on')

gpu = 1

for i in range(10):
    with time_block('CPU split_axis ...'): x_split = F.split_axis(x,1024,axis=0)
    with time_block('CPU concat ...'): x = F.concat(x_split,axis=0)
    with time_block('copy to GPU ...'): x = F.copy(x, gpu)
    with time_block('GPU split_axis ...'): x_split = F.split_axis(x,1024,axis=0)
    with time_block('GPU concat ...'): x = F.concat(x_split,axis=0)
    with time_block('copy to CPU ...'): x = F.copy(x, -1)
    print()