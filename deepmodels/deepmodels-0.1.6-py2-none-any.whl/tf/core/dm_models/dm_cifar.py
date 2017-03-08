"""DeepModels version of CIFAR.
"""

import os

from deepmodels.tf.core import commons
from deepmodels.tf.core import model_zoo
from deepmodels.shared.tools import data_manager


class CIFARDM(model_zoo.NetworkDM):
  """DeepModels version of CIFAR.
  """
  cifar10_params = commons.ModelParams(
      model_name=commons.ModelType.model_names[commons.ModelType.CIFAR10],
      model_type=commons.ModelType.CIFAR10,
      input_img_width=32,
      input_img_height=32,
      cls_num=10)
  cifar100_params = commons.ModelParams(
      model_name=commons.ModelType.model_names[commons.ModelType.CIFAR100],
      model_type=commons.ModelType.CIFAR100,
      input_img_width=32,
      input_img_height=32,
      cls_num=100)

  def __init__(self, net_type=commons.ModelType.CIFAR10):
    if net_type == commons.ModelType.CIFAR10:
      self.net_params = self.cifar10_params
    elif net_type == commons.ModelType.CIFAR100:
      self.net_params = self.cifar100_params
    else:
      raise ValueError("incorrect cifar type.")
    self.net_graph_fn = ""
    self.net_weight_fn = ""

  def get_label_names(self):
    proj_dir = data_manager.get_project_dir()
    if self.net_params.model_type == commons.ModelType.CIFAR10:
      label_fn = os.path.join(proj_dir, "tf/models/cifar/cifar10_labels.txt")
      label_name_dict = {}
      with open(label_fn, "r") as f:
        label_str = f.read()
        label_name_dict = eval(label_str)
      return label_name_dict
    else:
      raise ValueError("only cifar10 has named labels now.")
