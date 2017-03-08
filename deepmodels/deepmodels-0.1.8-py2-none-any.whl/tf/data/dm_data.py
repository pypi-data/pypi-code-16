"""Interface for defining data manager class for deepmodels.
"""

import abc

from deepmodels.tf.core import commons


class DMData(object):
  """Generic base class for defining a dataset manager class.
  """
  __metaclass__ = abc.ABCMeta

  def download(self):
    """Download data to local storage.
    """
    pass

  @abc.abstractmethod
  def create_base_data(self):
    """Create a basic structure of the data to work with.

    Examples like loading image data and labels to array
    before specific format for later use.
    """
    pass

  @abc.abstractmethod
  def get_data_for_clf(self,
                       data_type=commons.DataType.TRAIN,
                       batch_size=32,
                       target_img_height=128,
                       target_img_width=128,
                       preprocess_fn=None):
    """Create data for classification use.
    """
    pass
