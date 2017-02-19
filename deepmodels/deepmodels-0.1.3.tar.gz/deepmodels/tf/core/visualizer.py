"""Visualization for TensorFlow data.
"""

import tensorflow as tf

from deepmodels.tf.core import base_model


def vis_filter_activations(output_name, output_tensor):
  """Add filter activation to image summary.

  Args:
    output_name: name of the output layer.
    output_tensor: tensor of the output layer. It should have 4D shape.
  """
  # split into chunks of 3.
  tf.assert_equal(len(output_tensor.get_shape()), 4)
  num_splits = output_tensor.get_shape()[0] / 3
  acti_grids = tf.split(0, num_splits, output_tensor,
                        "{} split".format(output_name))
  for split_id in range(num_splits):
    summary_name = "{} split {}".format(output_name, split_id)
    tf.image_summary(summary_name, acti_grids[split_id], 3)


def vis_filter_weights(var_name, var_tensor):
  """Visualize filter weights.
  """
  pass
