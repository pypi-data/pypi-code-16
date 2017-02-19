"""Tests for DeepModels data.
"""

import os
import numpy as np

import tensorflow as tf
import tensorflow.contrib.slim as slim

from deepmodels.tf.core import commons
from deepmodels.tf.core import data_provider
from deepmodels.tf.core import model_zoo
from deepmodels.tf.core import tools

tf.logging.set_verbosity(tf.logging.INFO)


class TFDataTest(tf.test.TestCase):
  """Test dm data related stuff.
  """
  img_dir = "/mnt/DataHouse/Recognition/flower/flower_photos/"
  save_fn_prefix = "/mnt/DataHouse/Recognition/flower/flower"
  train_metadata_fn = tools.gen_metadata_filename(
      save_fn_prefix, commons.DataFileType.DATA_TRAIN)
  test_metadata_fn = tools.gen_metadata_filename(
      save_fn_prefix, commons.DataFileType.DATA_TEST)
  train_record_fn = save_fn_prefix + "__train.tfrecord"
  test_record_fn = save_fn_prefix + "__test.tfrecord"

  def test_img_metadata_gen(self):
    data_provider.gen_clf_metadata_from_img_fns(self.img_dir,
                                                self.save_fn_prefix)
    self.assertTrue(os.path.exists(train_fn))
    self.assertTrue(os.path.exists(test_fn))

  def test_img_fn_input(self):
    """Test batch image input.
    """
    # meta_fn = "/mnt/DataHouse/Fashion/EyeStyle/deepmodels_tf_data/eyestyle_092416__test.csv"
    meta_fn = "/home/jiefeng/datasets/fashion/dm_data/eyestyle__test.csv"
    batch_size = 12
    batch_data = data_provider.clf_input_from_image_fns(
        meta_fn, 3, 224, 224, batch_size, shuffle=True)
    img_batch, label_batch, fn_batch, _, _ = batch_data
    max_pixel_val = tf.reduce_max(img_batch)
    min_pixel_val = tf.reduce_min(img_batch)
    max_label_val = tf.reduce_max(label_batch)
    min_label_val = tf.reduce_min(label_batch)
    with self.test_session() as sess:
      sess.run(tf.initialize_all_variables())
      coord = tf.train.Coordinator()
      threads = tf.train.start_queue_runners(coord=coord)
      for i in range(20):
        print "batch {}:".format(i)
        cur_fn, cur_label = sess.run([fn_batch, label_batch])
        print cur_fn
        print cur_label
        print "max/min pixel values: {} {}".format(max_pixel_val.eval(),
                                                   min_pixel_val.eval())
        print "max/min label values: {} {}".format(max_label_val.eval(),
                                                   min_label_val.eval())
      coord.request_stop()
      coord.join(threads)

  def test_dataset_labels(self):
    pass

  def test_clf_tfrecord(self):
    """Test using tfrecord file as data file.
    """
    # create metadata file.

    data_provider.gen_clf_metadata_from_img_fns(self.img_dir,
                                                self.save_fn_prefix)
    # convert to tfrecord file.
    train_data_fn = tools.gen_metadata_filename(
        self.save_fn_prefix, commons.DataFileType.DATA_TRAIN)
    test_data_fn = tools.gen_metadata_filename(self.save_fn_prefix,
                                               commons.DataFileType.DATA_TEST)
    train_save_record = self.save_fn_prefix + "__train.tfrecord"
    test_save_record = self.save_fn_prefix + "__test.tfrecord"
    data_provider.convert_clf_data_to_tfrecord(train_data_fn,
                                               train_save_record)
    data_provider.convert_clf_data_to_tfrecord(test_data_fn, test_save_record)
    # load data from tfrecorde file.


if __name__ == "__main__":
  tf.test.main()
