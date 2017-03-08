"""MNIST data manager.
"""

import os
import cPickle as pickle
import gzip
import tarfile

import numpy as np

import tensorflow as tf

from six.moves import urllib


class MNISTData(object):
  """Class to manage MNIST data source.
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
    """Download MNIST data and unzip to a folder.
    """
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    mnist_url = "https://www.dropbox.com/s/i3a7apvb7wfk1v0/mnist.pkl.gz?dl=1"
    data_fn = mnist_url.split("/")[-1].split("?")[0]
    data_dir = os.path.join(cur_dir, "mnist")
    os.mkdir(data_dir)
    data_path = os.path.join(data_dir, data_fn)
    print "downloading mnist data, this may take some time..."
    filepath, _ = urllib.request.urlretrieve(mnist_url, data_path)
    statinfo = os.stat(filepath)
    print "Successfully downloaded", data_fn, statinfo.st_size, "bytes."

  def load_base_data(self):
    """Load original data from file.
    """
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    data_path = os.path.join(cur_dir, "mnist", "mnist.pkl.gz")
    with gzip.open(data_path, "rb") as f:
      data = pickle.load(f)

    self.train_imgs, self.train_labels = data[0]
    self.train_samp_num = len(self.train_labels)
    self.train_cls_num = len(set(self.train_labels))

    self.val_imgs, self.val_labels = data[1]

    self.test_imgs, self.test_labels = data[2]
    self.test_samp_num = len(self.test_labels)
    self.test_cls_num = len(set(self.test_labels))
    # reformat to images.
    self.train_imgs = self.train_imgs.reshape((-1, 1, 28, 28))
    self.val_imgs = self.val_imgs.reshape((-1, 1, 28, 28))
    self.test_imgs = self.test_imgs.reshape((-1, 1, 28, 28))

  def get_data_for_clf(self, data_type="train", batch_size=16, use_queue=True):
    """Get corresponding data for classification.

    Args:
      data_type: train or test.
    """
    if data_type == "train":
      if not use_queue:
        return self.train_imgs, self.train_labels, self.train_samp_num, self.train_cls_num
      else:
        data_tensor = tf.convert_to_tensor(self.train_imgs, tf.float32)
        label_tensor = tf.convert_to_tensor(self.train_labels, tf.int32)
        img_batch, label_batch = tf.train.shuffle_batch(
            [data_tensor, label_tensor],
            batch_size=batch_size,
            enqueue_many=True,
            capacity=batch_size * 20,
            min_after_dequeue=batch_size)
        return img_batch, label_batch, self.train_samp_num, self.train_cls_num
    else:
      if not use_queue:
        return self.test_imgs, self.test_labels, self.test_samp_num, self.test_cls_num
      else:
        data_tensor = tf.convert_to_tensor(self.test_imgs, tf.float32)
        label_tensor = tf.convert_to_tensor(self.test_labels, tf.int32)
        img_batch, label_batch = tf.train.shuffle_batch(
            [data_tensor, label_tensor],
            batch_size=batch_size,
            enqueue_many=True,
            capacity=batch_size * 20,
            min_after_dequeue=batch_size)
        return img_batch, label_batch, self.test_samp_num, self.test_cls_num


if __name__ == "__main__":
  mnist = MNISTData()
  # mnist.download()
  mnist.load_base_data()
