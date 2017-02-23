"""Common data definition.
"""

from abc import ABCMeta


class FeatType(object):
  """Feature type in python.
  """
  CNN_VGGS = 0,
  CNN_VGGS_SHORT = 1,
  CNN_VGG16 = 2,
  CNN_VGG16_SHORT = 3,
  CNN_ALEX = 4


class FeatParamsBase(object):
  """Base class for feature params.
  """
  feat_type = 0
  feat_name = ""


# map python feature type to c++ feature name.
FeatTypeToNameMapper = {
    FeatType.CNN_VGGS: "cnn_vggs",
    FeatType.CNN_VGGS_SHORT: "cnn_vggs_short",
    FeatType.CNN_VGG16: "cnn_vgg16",
    FeatType.CNN_VGG16_SHORT: "cnn_vgg16_short",
    FeatType.CNN_ALEX: "cnn_alex"
}


def map_name_to_feat_type(feat_name):
  """Map a feature name string to feature type.

  Args:
    feat_name: feature name string.
  """
  for py_type, name in FeatTypeToNameMapper.iteritems():
    if feat_name == name:
      return py_type
  raise ValueError("feat name not exist")


def is_cnn_feat(feat_name):
  """Check if a feature name is cnn feature.

  Args:
    feat_name: feature name string.
  """
  if feat_name in FeatTypeToNameMapper.values():
    return True
  else:
    return False


class BaseFeatParams(object):
  """Base class for feature extractor params.

  Put feature related params here.
  """
  pass


class BaseFeatExtractor(object):
  """Base class for feature extraction.

  Attributes:
    feat_params: feature parameters.
    raw_img_bgr: original bgr image.
    internal_img: intermediate image representation, e.g. gray image.
  """
  __metaclass__ = ABCMeta

  feat_params_ = None
  raw_img_bgr = None
  internal_img = None

  def init(self, feat_params):
    """Initialize feature extractor.

    Args:
      feat_params: parameters for feature extractor.
    """
    self.feat_params_ = feat_params

  def set_input(self, bgr_img):
    """Set input image.

    This is useful for repeated feature extraction from
    the same image with shared middle data.

    Args:
      bgr_img: color image with bgr pixels.
    """
    self.raw_img_bgr = bgr_img

  def start(self):
    """Prepare feature extractor.
    """
    pass

  def compute(self, bgr_img=None, mask=None):
    """Compute image feature.

    Args:
      bgr_img: input image. If none, use raw img.
      mask: pixel mask. non-zero indicates valid.
    Returns:
      feature vector.
    """
    pass

  def calc_dist(self, feat1, feat2):
    """Compute distance between two feature vectors.

    Used for custom distance metric.

    Args:
      feat1: first feature vector.
      feat2: second feature vector.
    Returns:
      float distance value.
    """
    pass
