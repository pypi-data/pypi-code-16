"""Manager for deepmodels models.
"""

from deepmodels.tf.core import commons

import dm_vgg
import dm_inception
import dm_cifar


def get_dm_model(model_type):
  """A factory to spawn deepmodels.

  Args:
    model_type: type of network model.
  Returns:
    corresponding deepmodel model object.
  """
  if commons.is_inception_model(model_type):
    incep = dm_inception.InceptionDM(model_type)
    return incep
  elif commons.is_vgg_model(model_type):
    vgg = dm_vgg.VGGDM(model_type)
    return vgg
  elif commons.is_cifar_model(model_type):
    cifar = dm_cifar.CIFARDM(model_type)
    return cifar
  else:
    raise ValueError("not supported model type.")
