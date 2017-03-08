import os
import numpy as np
import pickle
import matplotlib.pyplot as plt
import cv2
import caffe
import lasagne
print "Lasagne version:",lasagne.__version__
from lasagne.layers import InputLayer, DropoutLayer, FlattenLayer, DenseLayer, NonlinearityLayer, LocalResponseNormalization2DLayer
from lasagne.layers.dnn import Conv2DDNNLayer as ConvLayer # We have to use Conv2DDNNLayer
from lasagne.layers import Pool2DLayer as PoolLayer
from lasagne.utils import floatX
from lasagne.nonlinearities import rectify, softmax
from collections import OrderedDict

caffe_model_path='casia/casia_7pts_similarity_v2_iter_2000000.caffemodel'
#caffe_model_prototxt='casia/CASIA_deploy_pool5_flip.prototxt'
caffe_model_prototxt='casia/CASIA_deploy.prototxt'
nb_channels=1

# load caffe models
net_caffe = caffe.Net(caffe_model_prototxt, caffe_model_path, caffe.TEST)
print 'caffe model loaded.'

ignore_lrn=False
ignore_border_bool=False # what is the equivalent in caffe? False seems OK.

# create lasagne model
print 'building lasagne model'
net = {}
net['input'] = InputLayer((None, nb_channels, 100, 100))
net['conv11'] = ConvLayer(net['input'], num_filters=32, filter_size=3, pad=1, nonlinearity=rectify)
net['conv12'] = ConvLayer(net['conv11'], num_filters=64, filter_size=3, pad=1, nonlinearity=rectify)
net['norm1'] = LocalResponseNormalization2DLayer(net['conv12'], n=3, k=1, beta=0.75, alpha=0.0001)
net['pool1'] = PoolLayer(net['norm1'], pool_size=2, stride=2, mode='max', ignore_border=ignore_border_bool)
net['conv21'] = ConvLayer(net['pool1'], num_filters=64, filter_size=3, pad=1, nonlinearity=rectify)
net['conv22'] = ConvLayer(net['conv21'], num_filters=128, filter_size=3, pad=1, nonlinearity=rectify)
net['norm2'] = LocalResponseNormalization2DLayer(net['conv22'], n=3, k=1, beta=0.75, alpha=0.0001)
net['pool2'] = PoolLayer(net['norm2'], pool_size=2, stride=2, mode='max', ignore_border=ignore_border_bool)
net['conv31'] = ConvLayer(net['pool2'], num_filters=96, filter_size=3, pad=1, nonlinearity=rectify)
net['conv32'] = ConvLayer(net['conv31'], num_filters=192, filter_size=3, pad=1, nonlinearity=rectify)
net['pool3'] = PoolLayer(net['conv32'], pool_size=2, stride=2, mode='max', ignore_border=ignore_border_bool)
net['conv41'] = ConvLayer(net['pool3'], num_filters=128, filter_size=3, pad=1, nonlinearity=rectify)
net['conv42'] = ConvLayer(net['conv41'], num_filters=256, filter_size=3, pad=1, nonlinearity=rectify)
net['pool4'] = PoolLayer(net['conv42'], pool_size=2, stride=2, mode='max', ignore_border=ignore_border_bool)
net['conv51'] = ConvLayer(net['pool4'], num_filters=160, filter_size=3, pad=1, nonlinearity=rectify)
net['conv52'] = ConvLayer(net['conv51'], num_filters=320, filter_size=3, pad=1, nonlinearity=None)
net['pool5'] = PoolLayer(net['conv52'], pool_size=7, stride=1, mode='average_inc_pad', ignore_border=False) # or average_inc_pad
net['drop5'] = DropoutLayer(net['pool5'], p=0.4)
# If full prototxt
net['fc6'] = DenseLayer(net['drop5'], num_units=10549, nonlinearity=None)

# copy parameters
layers_caffe = dict(zip(list(net_caffe._layer_names), net_caffe.layers))
for name, layer in net.items():
    print name
    #print('caffe param dim: {}, {}'.format(layers_caffe[name].blobs[0].data.shape, layers_caffe[name].blobs[1].data.shape))
    try:
        #if name.startswith('fc'):
	if type(layer)==lasagne.layers.dense.DenseLayer:
	    print "Transposing weights for layer",name
            layer.W.set_value(layers_caffe[name].blobs[0].data.transpose())
        elif type(layer)==lasagne.layers.Conv2DLayer: # We should check if ConvLayer is cudnn or not...
       	    # flip filters when not using cudnn
	    print "Flipping fitlers because we do not use Conv2DDNNLayer for",name
            layer.W.set_value(layers_caffe[name].blobs[0].data[..., ::-1, ::-1])
        else:
            layer.W.set_value(layers_caffe[name].blobs[0].data)
        #layer.W.set_value(layers_caffe[name].blobs[0].data)
        layer.b.set_value(layers_caffe[name].blobs[1].data)       
    except AttributeError as e:
        print "Issue when setting weights for layer", name, str(e)
        continue

# test model, image should be gray level 100x100
scale_factor=0.00390625
# subtract mean and proper
mean_img_fn = 'casia/casia_mean_detok.npy'
mean_img = np.load(mean_img_fn)
mean_img = np.squeeze(mean_img)
#mean_img = np.transpose(mean_img,(1,0))
print 'testing model'
#test_fn = 'vgg_face_caffe/ak.png'
#test_fn='/media/03/JANUS_DATA/CASIAWebFace/OurNormalizedFaces_7pts_similarity/0000144/001.jpg'
#test_fn='/media/03/JANUS_DATA/CASIAWebFace/OurNormalizedFaces_7pts_similarity/0000349/008.jpg'
test_fn='/media/03/JANUS_DATA/CASIAWebFace/OurNormalizedFaces_7pts_similarity/0000411/041.jpg'
test_img = cv2.imread(test_fn)
if nb_channels==1:
    test_img=cv2.cvtColor(test_img,cv2.COLOR_BGR2GRAY)
    #test_img = np.transpose(test_img,(1,0))
test_img = np.float32(test_img)
input_img=(test_img-mean_img)*scale_factor
print input_img.shape
# convert to correct input format
input_lasagne=input_img
#input_lasagne=np.transpose(input_lasagne,(1,0))
if nb_channels==1:
    input_arr = np.array([[input_img]])
    input_lasagne = np.array([[input_lasagne]])
else:
    input_arr = np.array([np.transpose(input_img,(2,0,1))])
    input_lasagne = np.array([np.transpose(input_lasagne,(2,0,1))])
#cv2.imwrite('save.png', test_img)

face_name_fn = '/media/03/JANUS_DATA/CASIAWebFace/names_valid_JANUS.txt'
with open(face_name_fn, 'r') as f:
    face_names = f.readlines()
face_names = np.array(face_names)

net_caffe.blobs['data'].reshape(1, 1, 100, 100)
net_caffe.blobs['data'].data[:] = input_arr
net_caffe.forward()
pool5_caffe = net_caffe.blobs['pool5'].data.reshape(-1)
prob_caffe = net_caffe.blobs['fc6'].data.reshape(-1)
predicted_caffe = prob_caffe.argsort()[::-1][0:20]
probs_caffe = prob_caffe[predicted_caffe]

# print prob_caffe.shape
prob = np.array(lasagne.layers.get_output(net['fc6'], floatX(input_lasagne), deterministic=True).eval())
prob = prob.reshape(-1)
# print prob.shape
predicted = prob.argsort()[::-1][0:20]
probs = prob[predicted]

print "[PRED CAFFE]",predicted_caffe
print "[PRED LASAGNE]",predicted
print "[FC6 CAFFE]",probs_caffe
print "[FC6 LASAGNE]",probs

pool5 = np.array(lasagne.layers.get_output(net['pool5'], floatX(input_lasagne), deterministic=True).eval())
print "[POOL5 CAFFE]",np.squeeze(pool5_caffe)
print "[POOL5 LASAGNE]",np.squeeze(pool5)

for i in range(0, 20):
    pred_caffe = face_names[predicted_caffe[i]]
    pred_lasagne = face_names[predicted[i]]
    print('[CAFFE] {} - {} [LASAGNE]'.format(pred_caffe.rstrip(), pred_lasagne.rstrip()))

print "Done"

#Segmentation fault???
