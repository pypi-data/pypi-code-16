"""CIFAR data manager.
"""

import os
import cPickle as pickle
import tarfile

import numpy as np
from six.moves import urllib

import tensorflow as tf

from deepmodels.shared.tools import data_manager


class CIFAR10Data(object):
  """Class to manage CIFAR10 data source.
  """
  train_imgs = None
  train_labels = None
  train_samp_num = 0
  train_cls_num = 0
  test_imgs = None
  test_labels = None
  test_samp_num = 0
  test_cls_num = 0

  def __init__(self):
    pass

  def download(self):
    """Download CIFAR10 data and unzip to a folder.
    """
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    cifar10_url = "https://www.dropbox.com/s/eguzlh92mxjzfk0/cifar-10-python.tar.gz?dl=1"
    data_fn = cifar10_url.split("/")[-1].split("?")[0]
    data_dir = os.path.join(cur_dir, "cifar10")
    if os.path.exists(data_dir):
      return
    else:
      os.mkdir(data_dir)
    data_path = os.path.join(data_dir, data_fn)
    print "downloading cifar10 data, this may take some time..."
    filepath, _ = urllib.request.urlretrieve(cifar10_url, data_path)
    print()
    statinfo = os.stat(filepath)
    print("Successfully downloaded", data_fn, statinfo.st_size, "bytes.")
    # unzip file.
    tarfile.open(filepath, 'r:gz').extractall(cur_dir)
    print "tar unzipped."
    # remove downloaded file.
    os.remove(filepath)
    print "{} removed.".format(filepath)

  def load_base_data(self):
    """Load core data.
    """
    cur_fn_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(cur_fn_dir, "cifar-10-batches-py/")
    print "loading cifar-10 data from {}".format(data_dir)
    fns = {
        'train': [
            'data_batch_1', 'data_batch_2', 'data_batch_3', 'data_batch_4',
            'data_batch_5'
        ],
        'test': 'test_batch',
        'meta': 'batches.meta'
    }

    def format_data_for_cnn(data):
      """Data is a 2D numpy array, each row is a sample.
      """
      cnn_data = data.reshape((-1, 3, 32, 32))
      return cnn_data

    def load_one_fn(data_fn):
      """Load data from one file.
      """
      with open(data_fn, 'rb') as fn:
        data_dict = pickle.load(fn)
        # dict['data'] is a 2d numpy array; data['labels'] is a list
      return data_dict

    # training data
    train_data = []
    train_labels = []
    for cur_fn in fns["train"]:
      data = load_one_fn(data_dir + cur_fn)
      train_labels += data['labels']
      train_data.append(format_data_for_cnn(data['data']))
    train_data = np.concatenate(train_data).astype(np.float32)
    self.train_samp_num = train_data.shape[0]
    self.train_labels = np.asarray(train_labels, dtype=np.int64)
    self.train_cls_num = len(set(self.train_labels))
    # test data
    data = load_one_fn(data_dir + fns['test'])
    test_data = format_data_for_cnn(data['data']).astype(np.float32)
    self.test_samp_num = test_data.shape[0]
    self.test_labels = np.asarray(data['labels'], dtype=np.int64)
    self.test_cls_num = len(set(self.test_labels))
    # normalize
    train_data, mean, std = data_manager.normalize_imgs(train_data, None, None)
    test_data, _, _ = data_manager.normalize_imgs(test_data, mean, std)
    # format to tensorflow.
    self.train_imgs = np.transpose(train_data, (0, 2, 3, 1))
    self.test_imgs = np.transpose(test_data, (0, 2, 3, 1))
    print 'cifar10 loaded.'

  def get_data_for_clf(self,
                       data_type="train",
                       batch_size=16,
                       use_queue=True,
                       preprocess_fn=None):
    """Get corresponding data for classification.

    Args:
      data_type: train or test.
    """
    if data_type == "train":
      if not use_queue:
        return self.train_imgs, self.train_labels, self.train_samp_num, self.train_cls_num
      else:
        data_tensor = tf.convert_to_tensor(self.train_imgs, tf.float32)
        label_tensor = tf.convert_to_tensor(self.train_labels, tf.int64)
        img_data, img_label = tf.train.slice_input_producer(
            [data_tensor, label_tensor],
            num_epochs=None,
            shuffle=True,
            seed=161803)
        if preprocess_fn is not None:
          img_data = preprocess_fn(img_data, 32, 32)
        img_batch, label_batch = tf.train.shuffle_batch(
            [img_data, img_label],
            batch_size=batch_size,
            enqueue_many=False,
            capacity=batch_size * 20,
            min_after_dequeue=batch_size)
        return img_batch, label_batch, self.train_samp_num, self.train_cls_num
    else:
      if not use_queue:
        return self.test_imgs, self.test_labels, self.test_samp_num, self.test_cls_num
      else:
        data_tensor = tf.convert_to_tensor(self.test_imgs, tf.float32)
        label_tensor = tf.convert_to_tensor(self.test_labels, tf.int64)
        img_data, img_label = tf.train.slice_input_producer(
            [data_tensor, label_tensor],
            num_epochs=None,
            shuffle=True,
            seed=161803)
        if preprocess_fn is not None:
          img_data = preprocess_fn(img_data, 32, 32)
        img_batch, label_batch = tf.train.shuffle_batch(
            [img_data, img_label],
            batch_size=batch_size,
            enqueue_many=False,
            capacity=batch_size * 20,
            min_after_dequeue=batch_size)
        return img_batch, label_batch, self.test_samp_num, self.test_cls_num


if __name__ == "__main__":
  cifar10 = CIFAR10Data()
  cifar10.download()
