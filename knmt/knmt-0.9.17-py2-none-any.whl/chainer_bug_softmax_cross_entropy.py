import chainer
from chainer import Variable
import numpy as np

#create some random values for logits of 10 classes (minibatch size = 1)
logits = np.random.randn(1, 10).astype(np.float32)
target_valid = np.array([3], dtype = np.int32)
target_invalid = np.array([10], dtype = np.int32)

# create cpu variables
logits_cpu = Variable(logits)
target_valid_cpu = Variable(target_valid)
target_invalid_cpu = Variable(target_invalid)

#create gpu variables
logits_gpu = Variable(chainer.cuda.to_gpu(logits))
target_valid_gpu = Variable(chainer.cuda.to_gpu(target_valid))
target_invalid_gpu = Variable(chainer.cuda.to_gpu(target_invalid))



loss = chainer.functions.softmax_cross_entropy(logits_cpu, target_valid_cpu)
print "valid cpu loss is", loss.data
try:
    loss = chainer.functions.softmax_cross_entropy(logits_cpu, target_invalid_cpu)
    print "invalid cpu loss is", loss.data
except IndexError:
    print "cpu index check ok"
    

loss = chainer.functions.softmax_cross_entropy(logits_gpu, target_valid_gpu)
print "valid gpu loss is", loss.data


try:
    loss = chainer.functions.softmax_cross_entropy(logits_gpu, target_invalid_gpu)
    print "invalid gpu loss is", loss.data  # bug here: softmax_cross_entropy should not return a loss, but raise an exception
except IndexError:
    print "gpu index check ok"
