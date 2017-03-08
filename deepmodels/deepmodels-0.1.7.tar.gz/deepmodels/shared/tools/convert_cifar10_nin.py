import os
import numpy as np
import pickle
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2

try:
    user_paths = os.environ['PYTHONPATH'].split(os.pathsep)
except KeyError:
    user_paths = []
print(user_paths)
import caffe

import lasagne
from lasagne.layers import InputLayer, DropoutLayer, FlattenLayer, DenseLayer, NonlinearityLayer
#from lasagne.layers.dnn import Conv2DDNNLayer as ConvLayer # Not working for me
from lasagne.layers.conv import Conv2DLayer as ConvLayer
from lasagne.layers import Pool2DLayer as PoolLayer
from lasagne.utils import floatX
from lasagne.nonlinearities import rectify, softmax
from collections import OrderedDict

caffe_model_path='cifar10_nin/cifar10_nin.caffemodel'
caffe_model_prototxt='cifar10_nin/model.prototxt'

# load caffe models
net_caffe = caffe.Net(caffe_model_prototxt, caffe_model_path, caffe.TEST)
print 'caffe model loaded.'

# create lasagne model
print 'building lasagne model'
net = {}
net['input'] = InputLayer((None, 3, 32, 32))
net['conv1'] = ConvLayer(net['input'], num_filters=192, filter_size=5, pad=2)
net['cccp1'] = ConvLayer(net['conv1'], num_filters=160, filter_size=1)
net['cccp2'] = ConvLayer(net['cccp1'], num_filters=96, filter_size=1)
net['pool1'] = PoolLayer(net['cccp2'], pool_size=3, stride=2, mode='max', ignore_border=False)
net['drop3'] = DropoutLayer(net['pool1'], p=0.5)
net['conv2'] = ConvLayer(net['drop3'], num_filters=192, filter_size=5, pad=2)
net['cccp3'] = ConvLayer(net['conv2'], num_filters=192, filter_size=1)
net['cccp4'] = ConvLayer(net['cccp3'], num_filters=192, filter_size=1)
net['pool2'] = PoolLayer(net['cccp4'], pool_size=3, stride=2, mode='average_exc_pad', ignore_border=False)
net['drop6'] = DropoutLayer(net['pool2'], p=0.5)
net['conv3'] = ConvLayer(net['drop6'], num_filters=192, filter_size=3, pad=1)
net['cccp5'] = ConvLayer(net['conv3'], num_filters=192, filter_size=1)
net['cccp6'] = ConvLayer(net['cccp5'], num_filters=10, filter_size=1)
net['pool3'] = PoolLayer(net['cccp6'], pool_size=8, mode='average_exc_pad', ignore_border=False)
net['output'] = lasagne.layers.FlattenLayer(net['pool3'])

# copy parameters
print 'copy parameters from caffemodel to lasagne model'
layers_caffe = dict(zip(list(net_caffe._layer_names), net_caffe.layers))
#print "No real issues if only layer without weights raise errors"
for name, layer in net.items():
    print name
    #print('caffe param dim: {}, {}'.format(layers_caffe[name].blobs[0].data.shape, layers_caffe[name].blobs[1].data.shape))
    try:
        if name.startswith('fc'):
            layer.W.set_value(layers_caffe[name].blobs[0].data.transpose())
        elif name.startswith('conv'):
            # flip filters when not using cudnn
            layer.W.set_value(layers_caffe[name].blobs[0].data[..., ::-1, ::-1])
        else:
            layer.W.set_value(layers_caffe[name].blobs[0].data)
        layer.b.set_value(layers_caffe[name].blobs[1].data)       
    except AttributeError as e:
        print "Issue when setting weights for layer", name, str(e)
        continue

# test model
print 'testing model'
data = np.load('cifar10_nin/cifar10.npz')
num = 20
prob = np.array(lasagne.layers.get_output(net['output'], floatX(data['whitened'][0:]), deterministic=True).eval())
predicted = np.argmax(prob, 1)
accuracy = np.mean(predicted == data['labels'][0:])
print('lasagne accuracy: {}'.format(accuracy))

# get caffe output
net_caffe.blobs['data'].reshape(1000, 3, 32, 32)
net_caffe.blobs['data'].data[:] = data['whitened'][0:]
prob_caffe = net_caffe.forward()['pool3'][:,:,0,0]
print np.allclose(prob, prob_caffe)
caffe_pred = np.argmax(prob_caffe, 1)
print('caffe accuracy: {}'.format(np.mean(caffe_pred == data['labels'][0:])))

# for i in range(0, num):
#     true = data['CLASSES'][data['labels'][i]]
#     pred = data['CLASSES'][predicted[i]]
#     pred2 = data['CLASSES'][caffe_pred[i]]
#     print true, pred2, pred
    