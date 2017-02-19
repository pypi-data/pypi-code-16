#TO BE RUN with THEANO_FLAGS=mode=FAST_RUN,cuda.root=/usr/local/cuda-7.5,device=gpu,floatX=float32 python convert_vggface.py

import os
import numpy as np
import pickle
import matplotlib.pyplot as plt
import cv2
import caffe
import lasagne
print lasagne.__version__
from lasagne.layers import InputLayer, DropoutLayer, FlattenLayer, DenseLayer, NonlinearityLayer
from lasagne.layers.dnn import Conv2DDNNLayer as ConvLayer # We have to use Conv2DDNNLayer
from lasagne.layers import Pool2DLayer as PoolLayer
from lasagne.utils import floatX
from lasagne.nonlinearities import rectify, softmax, identity
from collections import OrderedDict

vggface_caffe_model_path='vgg_face_caffe/VGG_FACE.caffemodel'
vggface_caffe_model_prototxt='vgg_face_caffe/VGG_FACE_deploy.prototxt'

# load caffe models
net_caffe = caffe.Net(vggface_caffe_model_prototxt, vggface_caffe_model_path, caffe.TEST)
print 'caffe model loaded.'

# create lasagne model
print 'building lasagne model'
net = {}
net['input'] = InputLayer((None, 3, 224, 224))
net['conv1_1'] = ConvLayer(net['input'], num_filters=64, filter_size=3, pad=1, nonlinearity=None)
net['relu1_1'] = NonlinearityLayer(net['conv1_1'], nonlinearity=rectify)
net['conv1_2'] = ConvLayer(net['relu1_1'], num_filters=64, filter_size=3, pad=1, nonlinearity=rectify)
net['pool1'] = PoolLayer(net['conv1_2'], pool_size=2, stride=2, mode='max', ignore_border=False)
net['conv2_1'] = ConvLayer(net['pool1'], num_filters=128, filter_size=3, pad=1, nonlinearity=rectify)
net['conv2_2'] = ConvLayer(net['conv2_1'], num_filters=128, filter_size=3, pad=1, nonlinearity=rectify)
net['pool2'] = PoolLayer(net['conv2_2'], pool_size=2, stride=2, mode='max', ignore_border=False)
net['conv3_1'] = ConvLayer(net['pool2'], num_filters=256, filter_size=3, pad=1, nonlinearity=rectify)
net['conv3_2'] = ConvLayer(net['conv3_1'], num_filters=256, filter_size=3, pad=1, nonlinearity=rectify)
net['conv3_3'] = ConvLayer(net['conv3_2'], num_filters=256, filter_size=3, pad=1, nonlinearity=rectify)
net['pool3'] = PoolLayer(net['conv3_3'], pool_size=2, stride=2, mode='max', ignore_border=False)
net['conv4_1'] = ConvLayer(net['pool3'], num_filters=512, filter_size=3, pad=1, nonlinearity=rectify)
net['conv4_2'] = ConvLayer(net['conv4_1'], num_filters=512, filter_size=3, pad=1, nonlinearity=rectify)
net['conv4_3'] = ConvLayer(net['conv4_2'], num_filters=512, filter_size=3, pad=1, nonlinearity=rectify)
net['pool4'] = PoolLayer(net['conv4_3'], pool_size=2, stride=2, mode='max', ignore_border=False)
net['conv5_1'] = ConvLayer(net['pool4'], num_filters=512, filter_size=3, pad=1, nonlinearity=rectify)
net['conv5_2'] = ConvLayer(net['conv5_1'], num_filters=512, filter_size=3, pad=1, nonlinearity=rectify)
net['conv5_3'] = ConvLayer(net['conv5_2'], num_filters=512, filter_size=3, pad=1, nonlinearity=rectify)
net['pool5'] = PoolLayer(net['conv5_3'], pool_size=2, stride=2, mode='max', ignore_border=False)
net['fc6'] = DenseLayer(net['pool5'], num_units=4096, nonlinearity=rectify)
net['drop6'] = DropoutLayer(net['fc6'], p=0.5)
net['fc7'] = DenseLayer(net['drop6'], num_units=4096, nonlinearity=rectify)
net['drop7'] = DropoutLayer(net['fc7'], p=0.5)
net['fc8'] = DenseLayer(net['drop7'], num_units=2622, nonlinearity=None)
net['prob'] = lasagne.layers.NonlinearityLayer(net['fc8'], nonlinearity=softmax)

# copy parameters
layers_caffe = dict(zip(list(net_caffe._layer_names), net_caffe.layers))
for name, layer in net.items():
    try:
        if name.startswith('fc'):
            layer.W.set_value(layers_caffe[name].blobs[0].data.transpose())
        else:
            layer.W.set_value(layers_caffe[name].blobs[0].data)
        layer.b.set_value(layers_caffe[name].blobs[1].data)       
    except AttributeError:
        #print "Issue when setting weights for layer",name
        continue

# For consistency
net['output'] = lasagne.layers.NonlinearityLayer(net['prob'], nonlinearity=identity)

# test model
print 'testing model'
test_fn = 'vgg_face_caffe/ak.png'
test_img = cv2.imread(test_fn)
test_img = np.float32(test_img)
# convert to correct input format
b, g, r = cv2.split(test_img)
b -= 93.5940
g -= 104.7624
r -= 129.1863
test_img[:,:,0] = b
test_img[:,:,1] = g
test_img[:,:,2] = r
print test_img.shape
input_img = np.array([test_img])
print input_img.shape
input_img = input_img.transpose((0,3,1,2))
#cv2.imwrite('save.png', test_img)

face_name_fn = 'vgg_face_caffe/names.txt'
with open(face_name_fn, 'r') as f:
    face_names = f.readlines()
face_names = np.array(face_names)

save_fn='face_vgg.pkl'
params = lasagne.layers.get_all_param_values(net['output'])
data = {}
data['param_vals'] = params
data['class_names'] = face_names
data['mean_img'] = np.asarray([93.5940,104.7624,129.1863])
with open(save_fn, 'wb') as f:
	pickle.dump(data, f)
print('saved model to {}'.format(save_fn))


# check with caffe output, layer by layer
# for caffe_name in net_caffe._layer_names:
#     print caffe_name
net_caffe.blobs['data'].reshape(1, 3, 224, 224)
net_caffe.blobs['data'].data[:] = input_img
net_caffe.forward()
prob_caffe = net_caffe.blobs['prob'].data.reshape(-1)
predicted_caffe = prob_caffe.argsort()[::-1][0:20]
print predicted_caffe
probs_caffe = prob_caffe[predicted_caffe]
print probs_caffe

# print prob_caffe.shape
prob = np.array(lasagne.layers.get_output(net['prob'], floatX(input_img), deterministic=True).eval())


prob = prob.reshape(-1)
# print prob.shape
predicted = prob.argsort()[::-1][0:20]
print predicted
probs = prob[predicted]

for i in range(0, 20):
    pred_caffe = face_names[predicted_caffe[i]]
    pred_lasagne = face_names[predicted[i]]
    print('{}-{}'.format(pred_caffe.rstrip(), pred_lasagne.rstrip()))

print "Done"
#Segmentation fault???
