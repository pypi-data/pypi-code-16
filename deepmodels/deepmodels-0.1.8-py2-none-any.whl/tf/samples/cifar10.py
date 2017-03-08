"""Cifar10 example using DeepModels.
"""

import os
import numpy as np

import tensorflow as tf
import tensorflow.contrib.slim as slim

from deepmodels.tf.core import commons
from deepmodels.tf.core import common_flags
from deepmodels.tf.core.dm_models import dm_model_factory
from deepmodels.tf.core.learners import dm_classifier
from deepmodels.shared.tools import data_manager


from deepmodels.tf.data import cifar_data

tf.logging.set_verbosity(tf.logging.INFO)

flags = tf.app.flags
FLAGS = flags.FLAGS


class CIFARClf(dm_classifier.DMClassifier):
  """Only need to specify a dm model to use.
  """
  dm_model = dm_model_factory.get_dm_model(commons.ModelType.CIFAR10)


def main(_):
  clf = CIFARClf()
  cifardata = cifar_data.CIFAR10Data()
  cifardata.download()
  cifardata.load_base_data()

  if FLAGS.task == 0:
    img_batch, label_batch, samp_num, cls_num = cifardata.get_data_for_clf(
        batch_size=FLAGS.batch_size,
        preprocess_fn=clf.dm_model.get_preprocess_fn())
    clf.dm_model.net_params.cls_num = cls_num
    train_params = commons.TrainTestParams(
        log_dir=FLAGS.log_dir,
        samp_num=samp_num,
        batch_size=FLAGS.batch_size,
        opt_method=commons.OPTMethod.MOMENTUM,
        init_learning_rate=FLAGS.lrate,
        max_epochs=FLAGS.epochs,
        use_regularization=False)
    train_params.decay_steps = train_params.batch_num_per_epoch * 10
    clf.train(img_batch, label_batch, None, train_params)

  if FLAGS.task == 1:
    img_batch, label_batch, samp_num, cls_num = cifardata.get_data_for_clf(
        data_type="test",
        batch_size=FLAGS.batch_size,
        preprocess_fn=clf.dm_model.get_preprocess_fn())
    clf.dm_model.net_params.cls_num = cls_num
    test_params = commons.TrainTestParams(
        log_dir=FLAGS.log_dir,
        samp_num=samp_num,
        batch_size=FLAGS.batch_size,
        max_epochs=FLAGS.test_ratio)
    clf.test(img_batch, label_batch, None, test_params)


if __name__ == "__main__":
  tf.app.run()
