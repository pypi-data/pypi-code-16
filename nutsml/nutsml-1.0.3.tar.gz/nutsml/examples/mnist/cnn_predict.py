from __future__ import print_function

import numpy as np

from glob import glob
from cnn_train import create_network
from nutsflow import Collect, Consume, Get, Zip, Map
from nutsml import TransformImage, BuildBatch, ReadImage, ViewImageAnnotation

BATCH_SIZE = 128

transform = TransformImage(0).by('rerange', 0, 255, 0, 1, 'float32')
show_image = ViewImageAnnotation(0, 1, pause=1, figsize=(3, 3))
pred_batch = BuildBatch(BATCH_SIZE).by(0, 'image', 'float32')

print('loading network...')
network = create_network()
network.load_weights()

print('predicting...')
samples = glob('images/*.png') >> ReadImage(None) >> Collect()

predictions = (samples >> transform >> pred_batch >>
               network.predict() >> Map(np.argmax))
samples >> Get(0) >> Zip(predictions) >> show_image >> Consume()
