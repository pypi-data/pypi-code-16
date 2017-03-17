"""
Example nuts-ml pipeline for CIFAR-10 training and prediction
"""

import numpy as np
import cifarutil as cu

from nutsflow import *
from nutsml import *

NUM_EPOCHS = 100
BATCH_SIZE = 32
NUM_CLASSES = 10
INPUT_SHAPE = (3, 32, 32)


def create_network():
    from keras.models import Sequential
    from keras.layers import Dense, Dropout, Activation, Flatten
    from keras.layers import Convolution2D, MaxPooling2D

    model = Sequential()
    model.add(Convolution2D(32, 3, 3, border_mode='same',
                            input_shape=INPUT_SHAPE))
    model.add(Activation('relu'))
    model.add(Convolution2D(32, 3, 3))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.5))

    model.add(Convolution2D(64, 3, 3, border_mode='same'))
    model.add(Activation('relu'))
    model.add(Convolution2D(64, 3, 3))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.5))

    model.add(Flatten())
    model.add(Dense(512))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(NUM_CLASSES))
    model.add(Activation('softmax'))

    model.compile(loss='categorical_crossentropy',
                  optimizer='adam', metrics=['accuracy'])
    return KerasNetwork(model, filepath='weights_cifar10.hd5')


def train(train_samples, val_samples):
    from keras.metrics import categorical_accuracy

    rerange = TransformImage(0).by('rerange', 0, 255, 0, 1, 'float32')
    build_batch = (BuildBatch(BATCH_SIZE)
                   .by(0, 'image', 'float32')
                   .by(1, 'one_hot', 'uint8', NUM_CLASSES))
    p = 0.5
    augment = (AugmentImage(0)
               .by('identical', 1.0)
               .by('brightness', p, [0.7, 1.3])
               .by('color', p, [0.7, 1.3])
               .by('shear', p, [0, 0.1])
               .by('fliplr', p)
               .by('rotate', p, [-10, 10]))
    plot_eval = PlotLines((0, 1), layout=(2, 1))

    print 'creating network...'
    network = create_network()

    print 'training...', len(train_samples), len(val_samples)
    for epoch in xrange(NUM_EPOCHS):
        print 'EPOCH:', epoch

        t_results = (train_samples >> PrintProgress(train_samples) >>
                     Pick(0.2) >> augment >> rerange >>
                     build_batch >> network.train() >> Collect())
        t_loss, t_acc = zip(*t_results)
        print "training loss    :\t\t{:.6f}".format(np.mean(t_loss))
        print "training acc     :\t\t{:.1f}".format(100 * np.mean(t_acc))

        e_acc = (val_samples >> rerange >> build_batch
                 >> network.evaluate([categorical_accuracy]))
        print "evaluation acc   :\t\t{:.1f}".format(100 * e_acc)

        # network.save_best(e_acc, isloss=False)
        plot_eval((np.mean(t_acc), e_acc))
    print 'finished.'


def predict(val_samples, names):
    rerange = TransformImage(0).by('rerange', 0, 255, 0, 1, 'float32')
    show_image = ViewImageAnnotation(0, (1, 2), pause=2, figsize=(3, 3),
                                     interpolation='spline36')
    pred_batch = (BuildBatch(BATCH_SIZE).by(0, 'image', 'float32'))

    print 'creating network...'
    network = create_network()
    network.load_weights()

    print 'predicting...'
    samples = val_samples >> Take(1000) >> Collect()
    truelabels = samples >> Map(lambda (i, c, l): 'true: ' + names[c])
    predictions = (samples >> rerange >> pred_batch >> network.predict() >>
                   Map(ArgMax()) >> Map(lambda c: 'pred: ' + names[c]))
    samples >> Get(0) >> Zip(predictions, truelabels) >> show_image >> Consume()


def view(train_samples, names):
    show_image = ViewImageAnnotation(0, 1, pause=0.1,
                                     interpolation='spline36', figsize=(3, 3))
    Class2Name = nut_function(lambda (i, c, l): (i, names[c]))
    (train_samples >> Take(10) >> PrintTypeInfo() >> Class2Name() >>
     show_image >> Consume())


def load_data():
    datafolder = cu.download()
    names = cu.load_names(datafolder)
    samples = cu.load_samples(datafolder)
    train, val = samples >> PartitionByCol(2, ['train', 'test'])
    return names, train, val


if __name__ == "__main__":
    names, train_samples, val_samples = load_data()
    view(train_samples, names)
    train(train_samples, val_samples)
    predict(val_samples, names)
