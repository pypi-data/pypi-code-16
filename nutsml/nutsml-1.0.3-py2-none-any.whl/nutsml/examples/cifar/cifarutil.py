"""
Utils to download CIFAR data
"""

import urllib
import os
import tarfile
import cPickle

import numpy as np


def download(destfolder='temp'):
    def progress(blocknum, bs, size):
        print '\rdownloading %.0f%%' % (100.0 * blocknum * bs / size),

    tarfilename = 'cifar-10-python.tar.gz'
    tarfilepath = os.path.join(destfolder, tarfilename)
    untarfolder = os.path.join(destfolder, 'cifar-10')
    url = 'https://www.cs.toronto.edu/~kriz/' + tarfilename

    if not os.path.exists(tarfilepath) and not os.path.exists(untarfolder):
        urllib.urlretrieve(url, tarfilepath, progress)

    print 'untarring...',
    if not os.path.exists(untarfolder):
        with tarfile.open(tarfilepath, 'r:gz') as tfile:
            tfile.extractall(path=untarfolder)
    print 'done.'

    if os.path.exists(tarfilepath):
        os.remove(tarfilepath)

    return untarfolder


def load_batch(batchfilepath):
    with open(batchfilepath, 'rb') as f:
        batch = cPickle.load(f)
    data, labels = batch['data'], batch['labels']
    data = data.reshape(data.shape[0], 3, 32, 32)
    return data, labels


def load_names(datafolder):
    filepath = os.path.join(datafolder, 'cifar-10-batches-py', 'batches.meta')
    with open(filepath, 'rb') as f:
        return cPickle.load(f)['label_names']


def load_samples(datafolder):
    batchpath = os.path.join(datafolder, 'cifar-10-batches-py')
    from glob import glob
    for filepath in glob(batchpath + '/*_batch*'):
        data, labels = load_batch(filepath)
        fold = 'train' if 'data_batch' in filepath else 'test'
        for image, label in zip(data, labels):
            image = np.moveaxis(image, 0, 2)
            yield image, label, fold
