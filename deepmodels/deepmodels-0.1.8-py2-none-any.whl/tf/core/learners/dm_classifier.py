"""Template class for image classifier.
"""

import numpy as np

import tensorflow as tf
import tensorflow.contrib.slim as slim

from deepmodels.tf.core import commons
from deepmodels.tf.core import base_model
from deepmodels.tf.core import common_flags
from deepmodels.tf.core.learners.dm_learner import DMLearner
from deepmodels.shared.tools import data_manager

flags = tf.app.flags
FLAGS = flags.FLAGS


def comp_train_accuracy(pred_logits, label_batch):
  """Compute classification accuracy on training data.

  Args:
    pred_logits: prediction logits.
    label_batch: label batch.
  Returns:
    top 1 classfication accuracy.
  """

  # issue with img_folder_data that produces 2 dimensional label_batch
  label_batch = tf.squeeze(label_batch)
  pred_cls = tf.cast(tf.argmax(pred_logits, 1), tf.int32)
  correct_prediction = tf.cast(
      tf.equal(pred_cls, tf.cast(label_batch, tf.int32)), tf.float32)
  accuracy = tf.reduce_mean(correct_prediction)
  accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
  if tf.__version__ > '0.11':
    tf.summary.scalar("eval/mean_clf_accuracy", accuracy)
  else:
    tf.scalar_summary("eval/mean_clf_accuracy", accuracy)
  print "train/pred_cls_shape is: {}".format(tf.shape(pred_cls))
  print "train/label_batch_shape is: {}".format(tf.shape(label_batch))


# TODO(jiefeng): need a good way ensure user writes the exact same function
# header for overriding.
class DMClassifier(DMLearner):
  """Classifier template class.

  Work with general feature input or image feature.
  """

  def __init__(self):
    self.sess = tf.Session()

  def __del__(self):
    if self.sess is not None:
      self.sess.close()

  def compute_losses(self, gt_labels, pred_logits, endpoints):
    """Compute training losses.

    Override only when non-standard loss for a particular model.

    Args:
      gt_labels: ground truth labels in one-hot encoding.
      pred_logits: prediction logits.
      endpoints: endpoints from the model.
    Returns:
      computed loss tensor.
    """
    if tf.__version__ > '0.11':
      clf_loss = slim.losses.softmax_cross_entropy(
          pred_logits, gt_labels, weights=1.0, scope="clf_loss")
    else:
      clf_loss = slim.losses.softmax_cross_entropy(
          pred_logits, gt_labels, weight=1.0, scope="clf_loss")
    if tf.__version__ > '0.11':
      tf.summary.scalar("losses/clf_loss", clf_loss)
    else:
      tf.scalar_summary("losses/clf_loss", clf_loss)
    return clf_loss

  def train(self, train_input_batch, train_label_batch, model_params,
            train_params):
    """Training process of the classifier.

    Args:
      train_input_batch: input batch for training.
      train_label_batch: class id for training.
      model_params: commons.ModelParams object.
      train_params: commons.TrainTestParams object.
    """
    if self.dm_model is not None:
      # ignore input model params.
      model_params = self.dm_model.net_params
    pred_logits, endpoints = self.build_model(train_input_batch, model_params)
    self.set_key_vars(train_params.restore_scopes_exclude,
                      train_params.train_scopes)
    comp_train_accuracy(pred_logits, train_label_batch)
    tf.assert_equal(
        tf.reduce_max(train_label_batch),
        tf.convert_to_tensor(
            model_params.cls_num, dtype=tf.int64))
    onehot_labels = slim.one_hot_encoding(train_label_batch,
                                          model_params.cls_num)
    onehot_labels = tf.squeeze(onehot_labels)
    self.compute_losses(onehot_labels, pred_logits, endpoints)
    init_fn = None
    if train_params.fine_tune:
      init_fn = slim.assign_from_checkpoint_fn(train_params.custom["model_fn"],
                                               self.vars_to_restore)
    # this would not work if a tensorboard is running...
    if not train_params.resume_training:
      data_manager.remove_dir(train_params.train_log_dir)
    if train_params.use_regularization:
      regularization_loss = tf.add_n(slim.losses.get_regularization_losses())
      tf.scalar_summary("losses/regularization_loss", regularization_loss)

    total_loss = slim.losses.get_total_loss(
        add_regularization_losses=train_params.use_regularization)
    base_model.train_model_given_loss(
        total_loss, self.vars_to_train, train_params, init_fn=init_fn)

  def test(self, test_input_batch, test_label_batch, model_params,
           test_params):
    """Testing process of the classifier.

    Args:
      test_input_batch: input batch for testing.
      test_label_batch: class id for testing.
      model_params: commons.ModelParams object.
      test_params: commons.TrainTestParams object.
    """
    if self.dm_model is not None:
      model_params = self.dm_model.net_params
    pred_logits, _ = self.build_model(test_input_batch, model_params)
    pred_cls = tf.argmax(pred_logits, 1)
    metric_args = {
        "eval/mean_clf_accuracy":
        slim.metrics.streaming_accuracy(pred_cls, test_label_batch)
    }
    base_model.test_model_given_metrics(metric_args, test_params)

  def predict(self, input_data):
    """Get prediction value from a tensor.

    Args:
      input_data: inputs as numpy array to predict.
    Returns:
      two matrices with each row for each sample and
    ranked label id and probability.
    """
    cur_graph = tf.get_default_graph()
    output_tensor = cur_graph.get_tensor_by_name(self.output_tensor_name)
    pred_prob_tensor = tf.nn.softmax(output_tensor)
    pred_probs = self.get_output(input_data, pred_prob_tensor.name)
    sorted_pred_labels = np.argsort(pred_probs, axis=1)[:, ::-1]
    sorted_pred_probs = np.sort(pred_probs, axis=1)[:, ::-1]
    return sorted_pred_labels, sorted_pred_probs
