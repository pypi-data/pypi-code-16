"""High level interface to produce losses.
"""

import tensorflow as tf
import tensorflow.contrib.slim as slim

from deepmodels.tf.core import commons


def clf_loss(pred_logits,
             gt_labels,
             cls_num=10,
             loss_type=commons.LossType.CLF_SOFTMAX_HARD):
  """Compute classification loss.

  Args:
    pred_logits: logits prediction from a model.
    gt_labels: ground truth class labels.
    cls_num: number of classes.
    loss_type: specific type for the loss.
    SOFT if labels are probability. HARD if class id.
  Returns:
    computed loss.
  """
  with tf.variable_scope("clf_loss"):
    if loss_type == commons.LossType.CLF_SOFTMAX_HARD:
      # check labels are not exceeding cls_num.
      tf.assert_equal(tf.reduce_max(gt_labels), tf.convert_to_tensor(cls_num))
      soft_labels = slim.one_hot_encoding(gt_labels, cls_num)
    else:
      soft_labels = gt_labels
    clf_loss_elem = tf.nn.softmax_cross_entropy_with_logits(pred_logits,
                                                            soft_labels)
    mean_loss = tf.reduce_mean(clf_loss_elem, 0)
  return mean_loss


def triplet_loss(anchor_feats,
                 pos_feats,
                 neg_feats,
                 alpha=0.2,
                 loss_type=commons.LossType.TRIPLET_L2):
  """Compute triplet loss given triplet features.

  Args:
    anchor_feats: embedding of anchor points.
    pos_feats: embedding of positive points.
    neg_feats: embedding of negative points.
    alpha: margin value.
    loss_type: l1 or l2 triplet distance.
  """
  with tf.variable_scope("triplet_loss"):
    if loss_type == commons.LossType.TRIPLET_L2:
      # TODO(jiefeng): move normalization outside loss.
      anchor_normed = tf.nn.l2_normalize(anchor_feats, 1)
      pos_normed = tf.nn.l2_normalize(pos_feats, 1)
      neg_normed = tf.nn.l2_normalize(neg_feats, 1)
      pos_dist = tf.reduce_sum(tf.square(anchor_normed - pos_normed), 1)
      neg_dist = tf.reduce_sum(tf.square(anchor_normed - neg_normed), 1)

    if loss_type == commons.LossType.TRIPLET_L1:
      # TODO(jiefeng): do we need normalization here?
      pos_dist = tf.reduce_mean(tf.abs(anchor_feats - pos_feats), 1)
      neg_dist = tf.reduce_mean(tf.abs(anchor_feats - neg_feats), 1)

    # TRIPLET_HAMMING? check if features are binarize before?

    basic_loss = pos_dist - neg_dist + alpha
    loss = tf.reduce_mean(tf.maximum(basic_loss, 0.0))
  return loss
