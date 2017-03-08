"""Tests for dm learners.
"""

import tensorflow as tf

from deepmodels.tf.core import commons
from deepmodels.tf.core.learners.dm_classifier import DMClassifier
from deepmodels.tf.core.learners.dm_matcher import DMMatcher


class DMLearnerTester(tf.test.TestCase):
  def test_classifier(self):
    # create model object.
    my_clf = DMClassifier()
    # load data.
    # set model params.
    model_params = commons.ModelParams(
        "demo_model", model_type=commons.ModelType.CUSTOM, cls_num=10)
    # train.
    train_test_params = commons.TrainTestParams("", 1000)
    my_clf.train(None, None, model_params, train_test_params)

    # test.
    my_clf.test(None, None, model_params, train_test_params)

    # predict.
    inputs = tf.Placeholder(tf.float32)
    my_clf.build_model(inputs, model_params)

  def test_matcher(self):
    # create model object.
    my_matcher = DMMatcher()
    # load data.
    # set model params.
    model_params = commons.ModelParams(
        "demo_model", model_type=commons.ModelType.CUSTOM, cls_num=10)
    # train.
    train_test_params = commons.TrainTestParams("", 1000)
    my_matcher.train(None, None, None, model_params, train_test_params)
    # test.
    my_matcher.test(None, None, None, None, model_params, train_test_params)


if __name__ == "__main__":
  tf.test.main()
