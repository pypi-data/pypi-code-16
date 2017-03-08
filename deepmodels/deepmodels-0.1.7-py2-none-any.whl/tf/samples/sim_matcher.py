"""Similarity based feature embedding.
"""

import os
import sys

import tensorflow as tf
import tensorflow.contrib.slim as slim

from deepmodels.core import commons
from deepmodels.core.tf import base_model
from deepmodels.core.tf import data_provider
from deepmodels.core.tf import losses as dm_losses

tf.logging.set_verbosity(tf.logging.INFO)

flags = tf.app.flags
FLAGS = flags.FLAGS
flags.DEFINE_string("input_meta", "", "input meta data file.")
flags.DEFINE_float("margin_alpha", 0.2,
                   "margin between positive pair and negative pair.")


class SimpleMatcher(base_model.BaseDeepModel):
  """A template class for similarity based feature embedding.

  Learned with triplet loss.
  """

  def build_model(self, inputs, model_params):
    """Build a matching network.

    Args:
      inputs: input batch images.
      model_params: parameters for model.
    Returns:
      network embedded features.
    """
    pass

  def train_model(self, train_anchor_batch, train_pos_batch, train_neg_batch,
                  model_params, train_params):
    # get embedding for all batches.
    all_batch = tf.concat(
        0, [train_anchor_batch, train_pos_batch, train_neg_batch])
    with tf.variable_scope("matcher"):
      all_feats, _ = self.build_model(all_batch, model_params)
      anchor_feats, pos_feats, neg_feats = tf.split(0, 3, all_feats)
    # compute loss.
    triplet_loss = dm_losses.triplet_loss(
        anchor_feats,
        pos_feats,
        neg_feats,
        0.2,
        loss_type=commons.LossType.TRIPLET_L2)
    tf.scalar_summary("losses/triplet_loss", triplet_loss)
    # run training.
    base_model.train_model_given_loss(triplet_loss, None, train_params)

  # TODO (jiefeng): use proper evaluation for matcher and test.
  def test_model(self, test_anchor_batch, test_pos_batch, test_neg_batch,
                 model_params, test_params):
    # get embedding for all batches.
    with tf.variable_scope("matcher"):
      anchor_feats, _ = self.build_model(test_anchor_batch, model_params)
    with tf.variable_scope("matcher", reuse=True):
      pos_feats, _ = self.build_model(test_pos_batch, model_params)
      neg_feats, _ = self.build_model(test_neg_batch, model_params)
    # compute metrics: precision-recall.
    metric_args = {
        "eval/mean_clf_accuracy":
        slim.metrics.streaming_accuracy(pred_cls, test_label_batch)
    }
    base_model.test_model_given_metrics(metric_args, test_params)


def main(_):
  # create object.
  matcher = SimpleMatcher()
  model_params = base_model.create_model_params("demo_matcher")
  with tf.Graph().as_default():
    # prepare data.
    pass


if __name__ == "__main__":
  tf.app.run()