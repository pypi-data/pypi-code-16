"""Tests for DeepModels.
"""

#TODO(jiefeng): update this test or merge with dm_models tests.

import os
import numpy as np

from PIL import Image

import tensorflow as tf
import tensorflow.contrib.slim as slim
from tensorflow.python import pywrap_tensorflow

from deepmodels.tf.core import commons
from deepmodels.tf.core import base_model
from deepmodels.tf.core import model_zoo

tf.logging.set_verbosity(tf.logging.INFO)


class TFModelTest(tf.test.TestCase):
  """Test dm model related stuff.
  """

  def test_model_build(self):
    """Build model.
    """
    net_type = commons.ModelType.VGG16
    inputs = tf.placeholder(
        dtype=tf.float32,
        shape=(None, model_zoo.net_params[net_type].input_img_height,
               model_zoo.net_params[net_type].input_img_width, 3))
    model_zoo.build_net(net_type, inputs, commons.ModelMode.TEST)
    base_model.print_variable_names()
    with self.test_session():
      self.assertTrue(len(tf.all_variables()) > 0)

  def test_model_predict(self):
    """Test prediction using pretrained model.
    """
    # build model.
    net_type = commons.NetNames.VGG16
    img_width = model_zoo.net_params[net_type].input_img_width
    img_height = model_zoo.net_params[net_type].input_img_height
    inputs = tf.placeholder(
        dtype=tf.float32, shape=(1, img_height, img_width, 3))
    new_inputs = model_zoo.apply_batch_net_preprocess(net_type, inputs,
                                                      img_height, img_width)
    net_output, _ = model_zoo.build_net(
        net_type,
        new_inputs,
        cls_num=model_zoo.net_params[net_type].cls_num,
        mode=commons.ModelMode.TEST)
    net_pred = tf.nn.softmax(net_output)
    # prepare test image.
    img_fn = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "../../../data/imgs/car.jpg")
    test_img = Image.open(img_fn).resize((img_width, img_height))
    test_img = np.array(test_img)
    # test_img /= 255
    test_img = test_img.reshape(-1, img_height, img_width, 3)
    with self.test_session() as sess:
      saver = tf.train.Saver()
      saver.restore(sess, model_zoo.get_default_net_weights_fn(net_type))
      # OUTPUT: a list of one ndarray with shape (batch_size, cls_num).
      preds = sess.run([net_pred], feed_dict={inputs: test_img})
      # check if obey probability distribution
      preds = preds[0]
      # print preds
      print "best label: {}, score: {}".format(np.argmax(preds), np.max(preds))
      self.assertEqual(preds.shape[1], 1000, "incorrect prediction dim.")
      self.assertAlmostEqual(np.sum(preds), 1, places=3)
      self.assertTrue(np.all(np.greater_equal(preds, 0)))

  def test_model_restore(self):
    model_path = model_zoo.get_default_net_weights_fn(
        commons.NetNames.INCEPTION_V3)
    reader = pywrap_tensorflow.NewCheckpointReader(model_path)
    inputs = tf.placeholder(tf.float32, shape=(None, 299, 299, 3))
    model_zoo.build_net(commons.NetNames.INCEPTION_V3, inputs, 78)
    vars_to_restore = slim.get_variables_to_restore(
        exclude=["InceptionV3/Logits"])
    if isinstance(vars_to_restore, (tuple, list)):
      vars_to_restore = {var.op.name: var for var in vars_to_restore}
    for checkpoint_var_name in vars_to_restore:
      var = vars_to_restore[checkpoint_var_name]
      if not reader.has_tensor(checkpoint_var_name):
        raise ValueError('Checkpoint is missing variable [%s]' %
                         checkpoint_var_name)
      var_value = reader.get_tensor(checkpoint_var_name)
      print "tensor {} has shape {}, and its value has shape {}".format(
          checkpoint_var_name, var.get_shape(), var_value.shape)
      new_value = var_value.reshape(var.get_shape())


if __name__ == "__main__":
  tf.test.main()
