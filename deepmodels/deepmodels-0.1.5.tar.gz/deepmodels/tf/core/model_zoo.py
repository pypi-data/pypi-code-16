"""Definition of deep models.

Provide an organized structure for deep networks.
We will use existing slim model library so
will not reimplement them here.
"""

import abc
import os

import tensorflow as tf

from deepmodels.tf.core import commons
from deepmodels.shared.tools import data_manager

# this is comming from tf/core/models/slim
from nets import nets_factory
from preprocessing import preprocessing_factory


class NetworkDM(object):
  """Class template for metadata of a network.

  It contains information regarding the model itself,
  e.g. name, definition, labels etc.
  Good to be used together with a template to simplify process.
  """
  # __metaclass__ = abc.ABCMeta

  # network parameters.
  net_params = commons.ModelParams()
  # network data files.
  net_graph_fn = ""
  net_weight_fn = ""
  # mapping from predicted label to name string.
  net_label_names = {}

  def config_model(self, cls_num=None, mode=None):
    """Set model parameters.
    """
    if cls_num != None:
      self.net_params.cls_num = cls_num
    if mode != None:
      self.net_params.model_mode = mode

  def build_model(self, inputs, learner_type=commons.LearnerType.Classifier):
    """Define network model.
    """
    if learner_type == commons.LearnerType.Classifier:
      logits, endpoints = create_builtin_net(self.net_params.model_type,
                                             inputs, self.net_params.cls_num,
                                             self.net_params.model_mode)
      return logits, endpoints
    else:
      raise ValueError("only classifier is supported.")

  def get_preprocess_fn(self):
    """Obtain a corresponding preprocess function.
    """
    preprocess_fn = get_builtin_net_preprocess_fn(self.net_params.model_type,
                                                  self.net_params.model_mode)
    return preprocess_fn

  def get_label_names(self):
    """Obtain corresponding label names.
    """
    pass


def get_generic_preprocess_fn(scaling=False, whitening=True, distortion=False):
  """Create a generic preprocessing function.

  Args:
    scaling: scale image pixel to 0~1 value.
    whitening: apply per image whitening.
    distortion: apply distortion on image to create variations.
  """

  def preprocess_fn(img, target_width, target_height):
    img = tf.to_float(img)
    tf.image.resize(img, (target_height, target_width))
    return img

  return preprocess_fn


def is_tf_builtin_model_by_name(model_name):
  """Check if it is a built-in model from tf models.
  """
  tf_models = [
      "cifarnet", "inception_v1", "inception_v2", "inception_v3",
      "inception_v4", "vgg_16", "vgg_19", "alexnet_v2", "inception_resnet_v2"
  ]
  if model_name in tf_models:
    return True
  else:
    return False


def is_tf_builtin_model_by_type(model_type):
  """Check if it is a built-in model from tf models.
  """
  tf_models = [
      commons.ModelType.CIFAR10, commons.ModelType.INCEPTION_V1,
      commons.ModelType.INCEPTION_V2, commons.ModelType.INCEPTION_V3,
      commons.ModelType.INCEPTION_V4, commons.ModelType.VGG16,
      commons.ModelType.VGG19, commons.ModelType.ALEX_V2,
      commons.ModelType.INCEPTION_RESNET_V2
  ]
  if model_type in tf_models:
    return True
  else:
    return False


def create_builtin_net(model_type,
                       inputs,
                       cls_num,
                       mode=commons.ModelMode.TRAIN):
  """Build a network that is included in official model repo.

  Args:
    model_type: type of network.
    inputs: input tensor, batch or placeholder.
    cls_num: output class number.
    mode: model mode.
  Returns:
    net: network output.
    end_points: dictionary of named layer outputs.
  """
  if not is_tf_builtin_model_by_type(model_type):
    raise ValueError("net type is not supported.")

  # print "is training: {}".format(mode != commons.ModelMode.TEST)
  target_net = nets_factory.get_network_fn(
      commons.ModelType.model_names[model_type],
      cls_num,
      weight_decay=0.00004,
      is_training=mode != commons.ModelMode.TEST)
  logits, end_points = target_net(inputs)
  return logits, end_points


def get_builtin_net_weights_fn(model_type):
  """Retrieve built-in network weights file path.

  Used for loading weights.

  Args:
    model_type: type of network.
  Returns:
    network weight file.
  """
  if not is_tf_builtin_model_by_type(model_type):
    raise ValueError("net type is not supported.")
  proj_dir = data_manager.get_project_dir()
  ckpt_dir = os.path.join(proj_dir, "tf/models/",
                          commons.ModelType.model_names[model_type])
  # if not os.path.exists(ckpt_dir):
  #   raise ValueError("Default model data directory {} not exist."
  #                    " Run script under DeepModels/Models/ to set up.".format(
  #                        ckpt_dir))

  # ckpts = glob.glob(os.path.join(ckpt_dir, "*.ckpt*"))
  # ckpt = ckpts[0]
  ckpt = os.path.join(ckpt_dir,
                      commons.ModelType.model_names[model_type] + ".ckpt")
  return ckpt


def get_builtin_net_preprocess_fn(model_type,
                                  model_mode=commons.ModelMode.TRAIN):
  """Perform preprocess for a network.

  Args:
    model_type: type of network.
    target_width: target image width.
    target_height: target image height.
    model_mode: mode of the model.
  Returns:
    preprocess function for the given network.
  """
  if not is_tf_builtin_model_by_type(model_type):
    raise ValueError("net type is not supported.")
  preprocess_fn = preprocessing_factory.get_preprocessing(
      commons.ModelType.model_names[model_type],
      is_training=model_mode != commons.ModelMode.TEST)
  return preprocess_fn


def apply_batch_net_preprocess(inputs, preprocess_fn, target_width,
                               target_height):
  """Apply preprocess op to batch images.

  Args:
    inputs: batch images with shape (batch_size, h, w, ch).
    preprocess_fn: function with format (inputs, imgh, imgw).
    target_width: target image width.
    target_height: target image height.
  Returns:
    preprocessed batch images.
  """
  all_inputs = tf.unpack(inputs)
  processed_inputs = []
  for cur_input in all_inputs:
    new_input = preprocess_fn(cur_input, target_height, target_width)
    processed_inputs.append(new_input)
  new_inputs = tf.pack(processed_inputs)
  return new_inputs


# TODO(jiefeng): move to data related place?
# def net_label_names(net_type):
#   """Get label names for a network.

#   Args:
#     net_type: network type.
#   Returns:
#     a label to string dict for name mapping.
#   """
#   if net_type not in {
#       commons.ModelTypes.VGG16, commons.ModelTypes.INCEPTION_V3,
#       commons.ModelTypes.INCEPTION_V1
#   }:
#     raise ValueError("Only VGG16 labels are supported now.")
#   net_name = net_params[net_type].model_name
#   proj_dir = data_manager.get_project_dir()
#   label_fn = os.path.join(proj_dir, "models/{}/{}_labels.txt".format(net_name,
#                                                                      net_name))
#   label_name_dict = {}
#   with open(label_fn, "r") as f:
#     label_str = f.read()
#     label_name_dict = eval(label_str)
#     # label_names = f.readlines()
#     # label_name_dict = {i:label_names[i].rstrip() for i in range(len(label_names))}
#   return label_name_dict
